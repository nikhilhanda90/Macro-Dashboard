"""
Data Fetcher Module for Nikhil Market View
Retrieves economic data from Federal Reserve (FRED) and Eurostat
"""

import sys
import io

# Fix Windows console encoding issues (but not in Streamlit)
if sys.platform == 'win32' and not hasattr(sys.stdout, '_is_wrapped'):
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stdout._is_wrapped = True
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            sys.stderr._is_wrapped = True
    except (AttributeError, OSError):
        # Already wrapped or not available (e.g., in Streamlit)
        pass

import requests
import pandas as pd
from datetime import datetime, timedelta
try:
    import config_cycle_v2 as config
except ImportError:
    try:
        import config_cycle as config
    except ImportError:
        import config
import time

# Import Eurostat fetchers
try:
    from data_eurostat import EurostatFetcher
    EUROSTAT_AVAILABLE = True
except ImportError:
    EUROSTAT_AVAILABLE = False

try:
    from eurostat_fetcher_v2 import EurostatFetcher as EurostatFetcherV2
    EUROSTAT_V2_AVAILABLE = True
except ImportError:
    EUROSTAT_V2_AVAILABLE = False

try:
    from ecb_sdw_client import ECBSDWClient
    ECB_SDW_AVAILABLE = True
except ImportError:
    ECB_SDW_AVAILABLE = False

try:
    from fmp_client import FMPClient
    FMP_AVAILABLE = True
except ImportError:
    FMP_AVAILABLE = False


class DataFetcher:
    """Fetches economic data from various sources (FRED, Eurostat)"""
    
    def __init__(self):
        self.fred_api_key = config.FRED_API_KEY
        self.fred_base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.ecb_base_url = config.ECB_BASE_URL
        
        # Initialize Eurostat fetcher if available
        if EUROSTAT_AVAILABLE:
            self.eurostat = EurostatFetcher()
        else:
            self.eurostat = None
        
        # Initialize ECB SDW client if available
        if ECB_SDW_AVAILABLE:
            self.ecb_sdw = ECBSDWClient()
        else:
            self.ecb_sdw = None
        
        # Initialize FMP client if available
        if FMP_AVAILABLE:
            fmp_key = getattr(config, 'FMP_API_KEY', None)
            self.fmp = FMPClient(api_key=fmp_key)
        else:
            self.fmp = None
    
    def get_indicator(self, series_id, indicator_config):
        """
        Generic method to fetch any indicator (US or Eurozone)
        Supports both FRED and Eurostat sources with frequency-aware freshness
        
        Args:
            series_id: FRED series ID or Eurostat indicator name
            indicator_config: Config dict with name, category, source, etc.
            
        Returns:
            dict with data, name, category, etc., or None if data is stale/unavailable
        """
        # Check if this is a derived indicator (e.g., spread)
        source = indicator_config.get('source', 'fred')
        
        if source == 'derived_file':
            # Try to load pre-computed derived indicators from file (local dev)
            try:
                import pickle
                with open('derived_indicators.pkl', 'rb') as f:
                    derived_data = pickle.load(f)
                
                if series_id in derived_data:
                    df = derived_data[series_id]
                    # Ensure df has 'date' and 'value' columns
                    if 'date' not in df.columns:
                        df = df.reset_index()
                        df.columns = ['date', 'value']
                    print(f"  ✓ Loaded {series_id} from derived_indicators.pkl ({len(df)} obs)")
                    
                    # Return proper dict structure for dashboard
                    return {
                        'data': df,
                        'name': indicator_config.get('name', series_id),
                        'category': indicator_config.get('category', 'Unknown'),
                        'source': 'derived_file',
                        'series_id': series_id
                    }
                else:
                    print(f"  [SKIP] {series_id} not found in derived_indicators.pkl, trying fallback...")
                    # Fall through to compute on-the-fly
            except FileNotFoundError:
                print(f"  [INFO] derived_indicators.pkl not found - computing {series_id} on-the-fly (production mode)")
                # Fall through to compute on-the-fly
            except Exception as e:
                print(f"  [WARN] Error loading pickle: {e} - computing {series_id} on-the-fly")
                # Fall through to compute on-the-fly
            
            # FALLBACK: Compute spread on-the-fly (production mode)
            component_1 = indicator_config.get('spread_component_1')
            component_2 = indicator_config.get('spread_component_2')
            
            if not component_1 or not component_2:
                print(f"  [ERROR] {series_id} missing spread_component_1/2 metadata - cannot compute")
                return None
            
            print(f"  → Computing {series_id} = {component_1} - {component_2}")
            
            # Fetch both components
            df1 = self.get_fred_series(component_1, years_back=20)
            df2 = self.get_fred_series(component_2, years_back=20)
            
            if df1 is None or df2 is None:
                print(f"  [ERROR] Failed to fetch components for {series_id}")
                return None
            
            # Compute spread
            df1 = df1.rename(columns={'value': 'v1'})
            df2 = df2.rename(columns={'value': 'v2'})
            merged = pd.merge(df1, df2, on='date', how='inner')
            merged['value'] = merged['v1'] - merged['v2']
            
            spread_df = merged[['date', 'value']].copy()
            print(f"  ✓ Computed {series_id} on-the-fly ({len(spread_df)} obs)")
            
            # Return proper dict structure for dashboard
            return {
                'data': spread_df,
                'name': indicator_config.get('name', series_id),
                'category': indicator_config.get('category', 'Unknown'),
                'source': 'derived_on_fly',
                'series_id': series_id
            }
        
        elif source == 'derived':
            # Handle derived indicators (e.g., spreads)
            derived_type = indicator_config.get('derived_type', 'spread')
            
            if derived_type == 'spread':
                series_1_id = indicator_config.get('derived_series_1')
                series_2_id = indicator_config.get('derived_series_2')
                
                if not series_1_id or not series_2_id:
                    print(f"  [ERROR] Derived spread requires 'derived_series_1' and 'derived_series_2'")
                    return None
                
                # Fetch both series - find configs in INDICATOR_CONFIG_V2
                config_1 = next((item for item in config.INDICATOR_CONFIG_V2 if item.get('series_id') == series_1_id), None)
                config_2 = next((item for item in config.INDICATOR_CONFIG_V2 if item.get('series_id') == series_2_id), None)
                
                if not config_1 or not config_2:
                    print(f"  [ERROR] Could not find config for {series_1_id} or {series_2_id}")
                    return None
                
                result_1 = self.get_indicator(series_1_id, config_1)
                result_2 = self.get_indicator(series_2_id, config_2)
                
                if not result_1 or not result_2:
                    print(f"  [SKIP] Could not fetch both series for derived spread")
                    return None
                
                # Merge and calculate spread
                df_1 = result_1['data']
                df_2 = result_2['data']
                
                merged = pd.merge(df_1, df_2, on='date', suffixes=('_1', '_2'), how='inner')
                merged['value'] = merged['value_1'] - merged['value_2']  # Spread = series1 - series2
                
                df = merged[['date', 'value']].copy()
            else:
                print(f"  [ERROR] Unsupported derived_type: {derived_type}")
                return None
        
        # Check if this should come from Eurostat
        frequency = indicator_config.get('frequency', 'monthly')
        
        # Get frequency-aware freshness threshold
        freshness_thresholds = getattr(config, 'FRESHNESS_THRESHOLDS', {
            'daily': 3, 'weekly': 4, 'monthly': 6, 
            'quarterly': 9, 'annual': 18, 'irregular': 12
        })
        max_age_months = indicator_config.get('max_age_months') or freshness_thresholds.get(frequency, 6)
        
        if source == 'eurostat' and self.eurostat:
            # Fetch from Eurostat (old client)
            eurostat_name = indicator_config.get('eurostat_name', series_id)
            df = self.eurostat.get_indicator_by_name(eurostat_name, max_months=max_age_months)
        elif source == 'eurostat_v2' and EUROSTAT_V2_AVAILABLE:
            # Fetch from Eurostat v2 (working client for surveys)
            fetcher_v2 = EurostatFetcherV2()
            dataset_id = indicator_config.get('eurostat_dataset')
            geo = indicator_config.get('eurostat_geo', 'EA19')
            filters = indicator_config.get('eurostat_filters', {})
            
            series = fetcher_v2.fetch_series(dataset_id, geo, filters, last_n_periods=120)
            
            if series is not None and not series.empty:
                # Convert to DataFrame format
                df = pd.DataFrame({
                    'date': series.index,
                    'value': series.values
                }).reset_index(drop=True)
            else:
                df = None
        elif source == 'ecb_sdw' and self.ecb_sdw:
            # Fetch from ECB Statistical Data Warehouse
            maturity = indicator_config.get('ecb_maturity')  # e.g., '2Y', '5Y', '10Y'
            
            if maturity:
                series = self.ecb_sdw.fetch_yield(maturity, last_n_obs=2000)
                
                if series is not None and not series.empty:
                    # Convert to DataFrame format
                    df = pd.DataFrame({
                        'date': series.index,
                        'value': series.values
                    }).reset_index(drop=True)
                else:
                    df = None
            else:
                print(f"  [ERROR] ecb_sdw source requires 'ecb_maturity' in config")
                df = None
        elif source == 'fmp' and self.fmp:
            # Fetch from Financial Modeling Prep
            maturity = indicator_config.get('fmp_maturity')  # e.g., '2Y', '5Y', '10Y'
            symbol = indicator_config.get('fmp_symbol')      # e.g., '^GSPC', '^STOXX50E'
            
            if maturity:
                # Bond yield data
                series = self.fmp.fetch_bond_yield(maturity)
                
                if series is not None and not series.empty:
                    # Convert to DataFrame format
                    df = pd.DataFrame({
                        'date': series.index,
                        'value': series.values
                    }).reset_index(drop=True)
                else:
                    df = None
            elif symbol:
                # Equity index data
                series = self.fmp.fetch_equity_quote(symbol)
                
                if series is not None and not series.empty:
                    # Convert to DataFrame format
                    df = pd.DataFrame({
                        'date': series.index,
                        'value': series.values
                    }).reset_index(drop=True)
                else:
                    df = None
            else:
                print(f"  [ERROR] fmp source requires 'fmp_maturity' or 'fmp_symbol' in config")
                df = None
        elif source == 'ons':
            # Fetch from ONS (Office for National Statistics) Beta API
            try:
                from ons_client import ONSClient
                ons = ONSClient()
                dataset_id = indicator_config.get('ons_dataset')
                edition = indicator_config.get('ons_edition', 'time-series')
                dimensions = indicator_config.get('ons_dimensions', {})
                
                df = ons.get_time_series(dataset_id, edition=edition, dimensions=dimensions)
            except Exception as e:
                print(f"  [ERROR] ONS fetch failed for {series_id}: {e}")
                df = None
        elif source == 'boe':
            # Fetch from Bank of England IADB
            try:
                from boe_client import BoEClient
                boe = BoEClient()
                boe_series_code = indicator_config.get('boe_series_code', series_id)
                
                df = boe.get_series(boe_series_code, date_from='2000-01-01')
            except Exception as e:
                print(f"  [ERROR] BoE fetch failed for {series_id}: {e}")
                df = None
        elif source == 'csv':
            # Fetch from local CSV files
            try:
                from csv_data_loader import CSVDataLoader
                csv_loader = CSVDataLoader()
                df = csv_loader.load_series(series_id)
            except ImportError:
                print(f"  [ERROR] CSVDataLoader not available")
                df = None
            except Exception as e:
                print(f"  [ERROR] CSV load failed for {series_id}: {str(e)}")
                df = None
        else:
            # Fetch from FRED (default)
            df = self.get_fred_series(series_id)
            
            # Apply freshness check for FRED data too
            if df is not None and not df.empty:
                latest_date = df['date'].max()
                cutoff_date = datetime.now() - timedelta(days=max_age_months * 30.44)
                age_days = (datetime.now() - latest_date).days
                age_months = age_days / 30.44
                
                # DEBUG: Show last 5 timestamps
                last_5_dates = df['date'].tail(5).tolist()
                last_5_str = [d.strftime('%Y-%m-%d') for d in last_5_dates]
                
                if latest_date < cutoff_date:
                    # Data is stale - show debug info
                    print(f"\n  [STALE] {indicator_config.get('name')}")
                    print(f"    Source: {source.upper()}")
                    print(f"    Frequency: {frequency}")
                    print(f"    Last 5 dates: {', '.join(last_5_str)}")
                    print(f"    Latest: {latest_date.strftime('%Y-%m-%d')} ({age_days} days / {age_months:.1f} months old)")
                    print(f"    Cutoff: {cutoff_date.strftime('%Y-%m-%d')} (threshold: {max_age_months} months)")
                    print(f"    Status: EXCLUDED\n")
                    return None
                else:
                    # Data is fresh - brief log
                    print(f"  [FRESH] {indicator_config.get('name')} - Latest: {latest_date.strftime('%Y-%m-%d')} ({age_months:.1f}mo old, threshold: {max_age_months}mo)")
        
        if df is None or df.empty:
            return None
        
        return {
            'data': df,
            'name': indicator_config.get('name', series_id),
            'category': indicator_config.get('category', 'Other'),
            'description': indicator_config.get('description', ''),
            'frequency': indicator_config.get('frequency', 'unknown')
        }
        
    def get_fred_series(self, series_id, years_back=None):
        """
        Fetch data from FRED API
        
        Args:
            series_id: FRED series identifier
            years_back: Number of years of historical data (default from config)
            
        Returns:
            pandas DataFrame with date and value columns
        """
        if years_back is None:
            years_back = config.LOOKBACK_YEARS
            
        # Calculate observation start date
        observation_start = (datetime.now() - timedelta(days=365*years_back)).strftime('%Y-%m-%d')
        
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'observation_start': observation_start
        }
        
        try:
            response = requests.get(self.fred_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data:
                print(f"⚠️  No observations found for {series_id}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(data['observations'])
            
            # Clean data
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remove missing values
            df = df.dropna(subset=['value'])
            
            if df.empty:
                print(f"⚠️  No valid data for {series_id}")
                return None
                
            df = df[['date', 'value']].sort_values('date')
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {series_id}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {series_id}: {e}")
            return None
    
    def get_all_us_indicators(self):
        """
        Fetch all US economic indicators defined in config
        
        Returns:
            Dictionary with series_id as key and data info as value
        """
        results = {}
        total = len(config.US_INDICATORS)
        
        for idx, (series_id, info) in enumerate(config.US_INDICATORS.items(), 1):
            print(f"  [{idx}/{total}] Fetching {info['name']}...", end=' ')
            
            df = self.get_fred_series(series_id)
            
            # Handle backfilling (e.g., SOFR with LIBOR)
            if df is not None and info.get('backfill_series'):
                backfill_id = info['backfill_series']
                df_backfill = self.get_fred_series(backfill_id)
                if df_backfill is not None:
                    # Combine: use backfill data for earlier dates, main series for recent
                    df_combined = pd.concat([df_backfill, df]).sort_values('date')
                    # Remove duplicates, keeping the main series data
                    df_combined = df_combined.drop_duplicates(subset=['date'], keep='last')
                    df = df_combined
            
            if df is not None and not df.empty:
                results[series_id] = {
                    'data': df,
                    'name': info['name'],
                    'category': info['category'],
                    'description': info['description'],
                    'frequency': info['frequency']
                }
                print(f"OK ({len(df)} observations)")
            else:
                print("X Failed")
                results[series_id] = None
            
            # Rate limiting - be nice to FRED API
            time.sleep(0.2)
        
        return results
    
    def get_all_european_indicators(self):
        """
        Fetch all European economic indicators defined in config
        Note: European data is also available through FRED
        
        Returns:
            Dictionary with series_id as key and data info as value
        """
        results = {}
        total = len(config.EUROPEAN_INDICATORS)
        
        for idx, (series_id, info) in enumerate(config.EUROPEAN_INDICATORS.items(), 1):
            print(f"  [{idx}/{total}] Fetching {info['name']}...", end=' ')
            
            df = self.get_fred_series(series_id)
            
            if df is not None and not df.empty:
                results[series_id] = {
                    'data': df,
                    'name': info['name'],
                    'category': info['category'],
                    'description': info['description'],
                    'frequency': info['frequency']
                }
                print(f"OK ({len(df)} observations)")
            else:
                print("X Failed")
                results[series_id] = None
            
            # Rate limiting - be nice to FRED API
            time.sleep(0.2)
        
        return results
    
    def get_latest_value(self, series_id):
        """
        Get the most recent value for a series
        
        Args:
            series_id: FRED series identifier
            
        Returns:
            tuple: (value, date) or (None, None) if unavailable
        """
        df = self.get_fred_series(series_id, years_back=1)
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            return latest['value'], latest['date']
        
        return None, None
    
    def calculate_change(self, df, periods=1):
        """
        Calculate change over specified periods
        
        Args:
            df: DataFrame with date and value columns
            periods: Number of periods to look back
            
        Returns:
            Percentage change or None
        """
        if df is None or len(df) < periods + 1:
            return None
            
        current_value = df.iloc[-1]['value']
        previous_value = df.iloc[-(periods+1)]['value']
        
        if previous_value == 0:
            return None
            
        change = ((current_value - previous_value) / previous_value) * 100
        return change
    
    def get_year_over_year_change(self, series_id):
        """
        Calculate year-over-year percentage change
        
        Args:
            series_id: FRED series identifier
            
        Returns:
            YoY percentage change or None
        """
        df = self.get_fred_series(series_id, years_back=2)
        
        if df is None or df.empty:
            return None
        
        # Get monthly data and resample if needed
        df = df.set_index('date')
        
        # Resample to monthly if higher frequency
        if len(df) > 30:  # Likely daily or weekly data
            df = df.resample('M').last()
        
        if len(df) < 12:
            return None
        
        current_value = df.iloc[-1]['value']
        year_ago_value = df.iloc[-12]['value']
        
        if year_ago_value == 0:
            return None
        
        yoy_change = ((current_value - year_ago_value) / year_ago_value) * 100
        return yoy_change


    def get_all_european_indicators(self):
        """
        Fetch all European indicators from FRED
        (Most Eurozone data is available on FRED, easier than ECB API)
        
        Returns:
            Dictionary with series_id as key and data info as value
        """
        results = {}
        total = len(config.EUROPEAN_INDICATORS)
        
        print("\n📡 Fetching European economic data...")
        
        for idx, (series_id, info) in enumerate(config.EUROPEAN_INDICATORS.items(), 1):
            print(f"  [{idx}/{total}] Fetching {info['name']}...", end=' ')
            
            df = self.get_fred_series(series_id)
            
            if df is not None and not df.empty:
                results[series_id] = {
                    'data': df,
                    'name': info['name'],
                    'category': info['category'],
                    'description': info['description'],
                    'frequency': info['frequency']
                }
                print(f"OK ({len(df)} observations)")
            else:
                print("X Failed")
                results[series_id] = None
            
            # Rate limiting
            time.sleep(0.2)
        
        return results


# Convenience function for quick testing
def test_data_fetch():
    """Test function to verify data fetching works"""
    print("Testing FRED data fetch...")
    fetcher = DataFetcher()
    
    # Test with Federal Funds Rate
    df = fetcher.get_fred_series('DFF', years_back=5)
    
    if df is not None:
        print(f"OK Successfully fetched data: {len(df)} observations")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Latest value: {df['value'].iloc[-1]}")
        return True
    else:
        print("✗ Failed to fetch data")
        return False


if __name__ == "__main__":
    test_data_fetch()
