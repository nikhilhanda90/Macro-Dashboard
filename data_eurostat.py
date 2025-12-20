"""
Eurostat API Client for Nikhil Market View
Fetches economic data directly from Eurostat JSON API
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time

try:
    from cache_manager import CacheManager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class EurostatFetcher:
    """Fetches economic data from Eurostat API with local caching"""
    
    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
    
    # Comprehensive dataset configurations (geo will be overridden per fetch)
    DATASET_CONFIG = {
        "Real GDP": {
            "dataset_id": "NAMQ_10_GDP",
            "filters": {
                "na_item": "B1GQ",      # GDP
                "unit": "CLV_PCH_PRE",  # Chain linked volumes, % change previous period
                "s_adj": "SCA",         # Seasonally and calendar adjusted
                "geo": "EA19"           # Will be overridden
            },
            "frequency": "quarterly"
        },
        "Industrial Production": {
            "dataset_id": "STS_INPR_M",
            "filters": {
                "indic_bt": "PROD",     # Production index
                "nace_r2": "B-D",       # Industry
                "unit": "I15",          # Index 2015=100
                "s_adj": "NSA",         # Not seasonally adjusted
                "geo": "EA19"
            },
            "frequency": "monthly"
        },
        "Retail Trade Volume": {
            "dataset_id": "STS_TRTU_M",
            "filters": {
                "indic_bt": "TOVV",     # Turnover volume
                "nace_r2": "G47",       # Retail trade
                "unit": "I15",          # Index 2015=100
                "s_adj": "NSA",
                "geo": "EA19"
            },
            "frequency": "monthly"
        },
        "Construction Output": {
            "dataset_id": "STS_COPR_M",
            "filters": {
                "indic_bt": "PROD",     # Production
                "nace_r2": "F",         # Construction
                "unit": "I15",
                "s_adj": "NSA",
                "geo": "EA19"
            },
            "frequency": "monthly"
        },
        "Unemployment Rate": {
            "dataset_id": "UNE_RT_M",
            "filters": {
                "s_adj": "SA",          # Seasonally adjusted
                "age": "TOTAL",
                "unit": "PC_ACT",       # % of active population
                "sex": "T",             # Total
                "geo": "EA19"
            },
            "frequency": "monthly"
        },
        "Employment Level": {
            "dataset_id": "LFSQ_EGAN",
            "filters": {
                "age": "Y15-74",
                "sex": "T",
                "unit": "THS_PER",      # Thousands of persons
                "geo": "EA19"
            },
            "frequency": "quarterly"
        },
        "Economic Sentiment": {
            "dataset_id": "EI_BSSI_M_R2",
            "filters": {
                "indic": "ESI",         # Economic Sentiment Indicator
                "s_adj": "NSA",
                "geo": "EA19"
            },
            "frequency": "monthly"
        },
        "Consumer Confidence": {
            "dataset_id": "EI_BSCO_M",
            "filters": {
                "indic": "BS-CSMCI-BAL",  # Consumer confidence indicator
                "s_adj": "NSA",
                "geo": "EA19"
            },
            "frequency": "monthly"
        }
    }
    
    def __init__(self, use_cache: bool = True, cache_hours: int = 24):
        """
        Initialize Eurostat fetcher
        
        Args:
            use_cache: Whether to use local file cache
            cache_hours: Cache lifetime in hours
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Nikhil-Macro-Dashboard/1.0'
        })
        
        # Initialize cache
        self.use_cache = use_cache and CACHE_AVAILABLE
        self.cache_hours = cache_hours
        
        if self.use_cache:
            self.cache = CacheManager()
        else:
            self.cache = None
    
    def fetch_eurostat_dataset(
        self, 
        dataset_id: str, 
        filters: Optional[Dict[str, str]] = None,
        max_months: int = 60
    ) -> Optional[pd.Series]:
        """
        Calls Eurostat JSON API with caching, returns a pandas Series indexed by datetime.
        Only returns data where the latest timestamp is <= 6 months old.
        
        Args:
            dataset_id: Eurostat dataset code (e.g., "STS_INPR_M")
            filters: Dict of dimension filters (e.g., {"geo": "EA19", "freq": "M"})
            max_months: Maximum age in months for latest data point
            
        Returns:
            pandas Series with datetime index and values, or None if stale/unavailable
        """
        filters = filters or {}
        
        # Try to get from cache first (with 30-day data freshness check)
        if self.use_cache and self.cache:
            cached_series = self.cache.get_cached_data(
                dataset_id, 
                filters, 
                max_age_hours=self.cache_hours,
                data_freshness_days=30  # Force refresh if data > 30 days old
            )
            
            if cached_series is not None:
                # Verify cached data is still fresh enough for our use
                latest_date = cached_series.index.max()
                cutoff_date = datetime.now() - timedelta(days=max_months * 30.44)
                
                if latest_date >= cutoff_date:
                    print(f"  [CACHED] {dataset_id} ({len(cached_series)} obs, latest: {latest_date.strftime('%Y-%m-%d')})")
                    return cached_series
                else:
                    # Cached data exists but is too old for our freshness threshold
                    print(f"  [CACHE EXPIRED] {dataset_id}: latest {latest_date.strftime('%Y-%m-%d')} < cutoff {cutoff_date.strftime('%Y-%m-%d')}")
        
        # Cache miss or stale - fetch from API
        try:
            # Build query string from filters
            filter_str = "&".join([f"{k}={v}" for k, v in filters.items()])
            url = f"{self.BASE_URL}/{dataset_id}?{filter_str}&format=JSON"
            
            print(f"  [API] Fetching {dataset_id}...", end=' ')
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse JSON-stat format
            series = self._parse_jsonstat(data)
            
            if series is None or series.empty:
                print("X No data")
                return None
            
            # Apply freshness filter
            latest_date = series.index.max()
            cutoff_date = datetime.now() - timedelta(days=max_months * 30)
            
            if latest_date < cutoff_date:
                print(f"X Stale (latest: {latest_date.strftime('%Y-%m-%d')})")
                return None
            
            print(f"OK ({len(series)} obs, latest: {latest_date.strftime('%Y-%m-%d')})")
            
            # Save to cache for next time
            if self.use_cache and self.cache:
                self.cache.save_to_cache(dataset_id, filters, series)
            
            return series
            
        except requests.exceptions.RequestException as e:
            print(f"X Request error: {e}")
            return None
        except Exception as e:
            print(f"X Parse error: {e}")
            return None
    
    def _parse_jsonstat(self, data: Dict[str, Any]) -> Optional[pd.Series]:
        """
        Parse Eurostat JSON-stat format into pandas Series
        
        Args:
            data: JSON response from Eurostat API
            
        Returns:
            pandas Series with datetime index
        """
        try:
            # Eurostat API can return different formats
            # Try to handle both JSON-stat and simpler formats
            
            # Check if we have the standard structure
            if not isinstance(data, dict):
                return None
            
            # Try JSON-stat format first
            if 'dimension' in data and 'value' in data:
                return self._parse_jsonstat_standard(data)
            
            # Try alternative format
            if 'value' in data and isinstance(data['value'], dict):
                return self._parse_jsonstat_alt(data)
            
            return None
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    def _parse_jsonstat_standard(self, data: Dict[str, Any]) -> Optional[pd.Series]:
        """Parse standard JSON-stat format"""
        try:
            dimensions = data['dimension']
            values = data['value']
            
            # Find time dimension
            time_key = None
            for key in ['time', 'TIME_PERIOD', 'Time']:
                if key in dimensions:
                    time_key = key
                    break
            
            if not time_key:
                return None
            
            time_category = dimensions[time_key]['category']
            time_indices = time_category['index']
            
            # Build series
            dates = []
            vals = []
            
            for time_label in time_indices.keys():
                dt = self._parse_time_label(time_label)
                if dt is None:
                    continue
                
                idx = time_indices[time_label]
                
                # Get value
                if isinstance(values, dict):
                    val = values.get(str(idx))
                elif isinstance(values, list):
                    val = values[idx] if idx < len(values) else None
                else:
                    continue
                
                if val is not None:
                    try:
                        dates.append(dt)
                        vals.append(float(val))
                    except (ValueError, TypeError):
                        continue
            
            if not dates:
                return None
            
            series = pd.Series(vals, index=pd.DatetimeIndex(dates))
            return series.sort_index()
            
        except Exception as e:
            print(f"Standard parse error: {e}")
            return None
    
    def _parse_jsonstat_alt(self, data: Dict[str, Any]) -> Optional[pd.Series]:
        """Parse alternative JSON format"""
        try:
            values = data['value']
            
            # Values dict has keys like "0", "1", etc.
            # Need to map to time periods from dimension
            if 'dimension' not in data:
                return None
            
            # This is a simplified parser - might need adjustment
            return None
            
        except Exception:
            return None
    
    def _parse_time_label(self, time_label: str) -> Optional[datetime]:
        """
        Convert Eurostat time label to datetime with CORRECT quarter-end dates
        
        Handles formats:
        - "2024M01" -> 2024-01-31 (end of month)
        - "2024Q1" -> 2024-03-31 (end of Q1)
        - "2024Q2" -> 2024-06-30 (end of Q2)
        - "2024Q3" -> 2024-09-30 (end of Q3)
        - "2024Q4" -> 2024-12-31 (end of Q4)
        - "2024" -> 2024-12-31 (end of year)
        
        Args:
            time_label: Time string from Eurostat
            
        Returns:
            datetime object at END of period or None
        """
        try:
            # Monthly: "2024M01" or "2024-01"
            if 'M' in time_label:
                year, month = time_label.split('M')
                # Use end of month (last day)
                dt = pd.Period(f"{year}-{month}", freq='M').to_timestamp(how='end')
                return dt
            
            # Quarterly: "2024Q1" - CRITICAL: Map to quarter END dates
            elif 'Q' in time_label:
                year, quarter = time_label.split('Q')
                quarter_num = int(quarter)
                
                # Map quarter to correct end month
                quarter_end_months = {1: 3, 2: 6, 3: 9, 4: 12}
                end_month = quarter_end_months[quarter_num]
                
                # Create end-of-quarter date (last day of end month)
                dt = pd.Period(f"{year}-{end_month:02d}", freq='M').to_timestamp(how='end')
                return dt
            
            # Annual: "2024"
            elif len(time_label) == 4 and time_label.isdigit():
                return pd.Timestamp(int(time_label), 12, 31)
            
            # Try standard date parsing
            else:
                return pd.to_datetime(time_label)
                
        except Exception as e:
            print(f"Error parsing time label '{time_label}': {e}")
            return None
    
    def get_indicator_by_name(
        self, 
        indicator_name: str, 
        geo: str = "EA19",
        max_months: int = 6
    ) -> Optional[pd.DataFrame]:
        """
        Fetch indicator by friendly name using predefined configs
        
        Args:
            indicator_name: Name from DATASET_CONFIG keys
            geo: Geographic area code (EA19, DE, FR, etc.)
            max_months: Maximum age in months for freshness check
            
        Returns:
            DataFrame with 'date' and 'value' columns, or None
        """
        config = self.DATASET_CONFIG.get(indicator_name)
        if not config:
            print(f"X Unknown indicator: {indicator_name}")
            return None
        
        # Override geo in filters
        filters = config.get('filters', {}).copy()
        filters['geo'] = geo
        
        series = self.fetch_eurostat_dataset(
            config['dataset_id'],
            filters,
            max_months=max_months
        )
        
        if series is None or series.empty:
            return None
        
        # Convert Series to DataFrame with 'date' and 'value' columns
        df = pd.DataFrame({
            'date': series.index,
            'value': series.values
        }).reset_index(drop=True)
        
        return df
    
    def get_indicator_multi_geo(
        self,
        indicator_name: str,
        geos: list = ["EA19", "DE", "FR"],
        max_months: int = 6
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch indicator for multiple geographic areas
        
        Args:
            indicator_name: Name from DATASET_CONFIG keys
            geos: List of geographic area codes
            max_months: Maximum age in months for freshness check
            
        Returns:
            Dict mapping geo code to DataFrame (or None if stale/unavailable)
        """
        results = {}
        for geo in geos:
            results[geo] = self.get_indicator_by_name(
                indicator_name, 
                geo=geo, 
                max_months=max_months
            )
        return results


def test_eurostat_fetch():
    """Test function to verify Eurostat fetching works"""
    print("\n" + "="*80)
    print("Testing Eurostat API Client")
    print("="*80 + "\n")
    
    fetcher = EurostatFetcher()
    
    # Test a few indicators
    test_indicators = [
        "Industrial Production",
        "Consumer Confidence",
        "Real GDP",
        "Unemployment Rate"
    ]
    
    for indicator in test_indicators:
        df = fetcher.get_indicator_by_name(indicator, max_months=6)
        if df is not None and not df.empty:
            print(f"  Latest: {df.iloc[-1]['date'].strftime('%Y-%m-%d')} = {df.iloc[-1]['value']:.2f}")
        print()
    
    print("="*80)


if __name__ == "__main__":
    test_eurostat_fetch()

