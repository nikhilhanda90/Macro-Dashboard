"""
CSV Data Loader for Eurozone Indicators
Handles various CSV formats from Eurostat, ECB, and Trading Economics
"""

import pandas as pd
import os
from datetime import datetime
from typing import Optional, Dict
import config_cycle_v2 as config


class CSVDataLoader:
    """
    Load and parse CSV files for Eurozone indicators
    """
    
    def __init__(self, csv_directory: str = "eurozone_data"):
        self.csv_dir = csv_directory
        
        # Mapping of indicator IDs to CSV files
        self.csv_mapping = {
            'EA_UNEMPLOYMENT': 'eurostat_unemployment_ea20.csv',
            'EA_EMPLOYMENT': 'eurostat_employment_ea20.csv',
            'EA_IP': 'eurostat_ip_ea20.csv',
            'EA_MFG_PMI': 'eurozone_mfg_pmi.csv',
            'EA_RETAIL': 'eurostat_retail_ea20.csv',
            'EA_HOUSE_PRICES': 'eurostat_house_prices_ea20.csv',
            'EA_ULC': 'eurostat_ulc_ea20.csv',
            'EA_COMPENSATION': 'ecb_compensation_ea.csv',
            'EA_HICP_HEADLINE': 'eurostat_hicp_headline_ea20.csv',
            'EA_INDUSTRIAL_CONF': 'eurostat_industrial_confidence_ea20.csv',
            'EA_YIELD_CURVE': 'ecb_yield_curve_full.csv',
        }
    
    def load_series(self, indicator_id: str) -> Optional[pd.DataFrame]:
        """
        Load a CSV series by indicator ID
        
        Returns:
            DataFrame with 'date' and 'value' columns, or None if not found
        """
        
        if indicator_id not in self.csv_mapping:
            return None
        
        filename = self.csv_mapping[indicator_id]
        filepath = os.path.join(self.csv_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"[CSV] File not found: {filepath}")
            return None
        
        try:
            # Try different parsers based on filename or indicator type
            # ULC and Compensation are from ECB even if filename says eurostat
            if indicator_id in ['EA_ULC', 'EA_COMPENSATION']:
                df = self._parse_ecb_csv(filepath)
            elif 'eurostat' in filename.lower():
                df = self._parse_eurostat_csv(filepath)
            elif 'ecb' in filename.lower():
                df = self._parse_ecb_csv(filepath)
            elif 'pmi' in filename.lower():
                df = self._parse_trading_economics_csv(filepath)
            else:
                df = self._parse_generic_csv(filepath)
            
            if df is not None and len(df) > 0:
                print(f"[CSV] Loaded {indicator_id}: {len(df)} obs, latest: {df['date'].max()}")
                return df
            else:
                print(f"[CSV] No data parsed from {filename}")
                return None
                
        except Exception as e:
            print(f"[CSV ERROR] {indicator_id}: {str(e)}")
            return None
    
    def _parse_eurostat_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Parse Eurostat CSV format
        
        Eurostat CSVs can be in two formats:
        1. Long format: TIME_PERIOD and OBS_VALUE columns (one row per observation)
        2. Wide format: Time periods as columns (rare)
        """
        
        try:
            # Read the full CSV
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # Check for long format (most common)
            if 'TIME_PERIOD' in df.columns and 'OBS_VALUE' in df.columns:
                # Long format - easy!
                result = pd.DataFrame({
                    'date': pd.to_datetime(df['TIME_PERIOD'], errors='coerce'),
                    'value': pd.to_numeric(df['OBS_VALUE'], errors='coerce')
                })
                
                result = result.dropna(subset=['date', 'value'])
                result = result.sort_values('date').reset_index(drop=True)
                
                return result
            
            # Otherwise, try wide format (time periods as columns)
            date_cols = [col for col in df.columns if self._is_date_column(col)]
            
            if not date_cols:
                print(f"[WARN] No date columns found in {filepath}")
                return None
            
            # Melt the dataframe to long format
            id_cols = [col for col in df.columns if col not in date_cols]
            
            if len(id_cols) == 0:
                # Pure time series (rare)
                melted = pd.DataFrame({
                    'date': date_cols,
                    'value': [df[col].iloc[0] if len(df) > 0 else None for col in date_cols]
                })
            else:
                # Standard format with metadata columns
                melted = df.melt(id_vars=id_cols, value_vars=date_cols, 
                                var_name='date', value_name='value')
            
            # Clean up
            melted = melted[['date', 'value']].copy()
            melted['date'] = pd.to_datetime(melted['date'], errors='coerce')
            melted['value'] = pd.to_numeric(melted['value'], errors='coerce')
            
            # Drop missing
            melted = melted.dropna(subset=['date', 'value'])
            melted = melted.sort_values('date').reset_index(drop=True)
            
            return melted
            
        except Exception as e:
            print(f"[ERROR] Eurostat parse failed: {str(e)}")
            return None
    
    def _parse_ecb_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Parse ECB SDW CSV format
        
        ECB CSVs typically have:
        - Clean format with date column
        - May have multiple series (need to filter)
        """
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # ECB usually has 'DATE' or 'TIME_PERIOD' or 'Date' column
            date_col = None
            for col in ['DATE', 'TIME_PERIOD', 'Date', 'date', 'TIME', 'PERIOD']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print(f"[WARN] No date column found in ECB CSV")
                return None
            
            # Find value column - could be third column or have specific names
            value_col = None
            
            # Try common value column names
            for col in ['OBS_VALUE', 'Value', 'value', 'YIELD', 'INDEX']:
                if col in df.columns:
                    value_col = col
                    break
            
            # If no standard name, use third column (ECB often puts data in 3rd column)
            if value_col is None and len(df.columns) >= 3:
                value_col = df.columns[2]  # Third column (0-indexed)
            
            if value_col is None:
                print(f"[WARN] No value column found in ECB CSV")
                return None
            
            # Extract date and value
            result = pd.DataFrame({
                'date': pd.to_datetime(df[date_col], errors='coerce'),
                'value': pd.to_numeric(df[value_col], errors='coerce')
            })
            
            result = result.dropna(subset=['date', 'value'])
            result = result.sort_values('date').reset_index(drop=True)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] ECB parse failed: {str(e)}")
            return None
    
    def _parse_trading_economics_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Parse Trading Economics CSV format
        
        Usually has:
        - 'Date' or 'date' column
        - 'Value' or indicator name column
        """
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # Find date column
            date_col = None
            for col in ['Date', 'date', 'TIME', 'Period']:
                if col in df.columns:
                    date_col = col
                    break
            
            # Find value column (usually second column or named 'Value')
            value_col = None
            if 'Value' in df.columns:
                value_col = 'Value'
            elif len(df.columns) >= 2:
                value_col = df.columns[1]  # Second column
            
            if date_col is None or value_col is None:
                print(f"[WARN] Could not find date/value columns")
                return None
            
            result = pd.DataFrame({
                'date': pd.to_datetime(df[date_col], errors='coerce'),
                'value': pd.to_numeric(df[value_col], errors='coerce')
            })
            
            result = result.dropna(subset=['date', 'value'])
            result = result.sort_values('date').reset_index(drop=True)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Trading Economics parse failed: {str(e)}")
            return None
    
    def _parse_generic_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Generic CSV parser - try to auto-detect format
        """
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # Assume first column is date, second is value
            if len(df.columns) < 2:
                return None
            
            result = pd.DataFrame({
                'date': pd.to_datetime(df.iloc[:, 0], errors='coerce'),
                'value': pd.to_numeric(df.iloc[:, 1], errors='coerce')
            })
            
            result = result.dropna(subset=['date', 'value'])
            result = result.sort_values('date').reset_index(drop=True)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Generic parse failed: {str(e)}")
            return None
    
    def _is_date_column(self, col_name: str) -> bool:
        """
        Check if a column name looks like a date
        
        Examples: '2020-01', '2020Q1', '2020M01', '2020'
        """
        
        col_str = str(col_name)
        
        # Check for year at start (20XX or 19XX)
        if col_str.startswith('20') or col_str.startswith('19'):
            return True
        
        # Check for common date patterns
        date_indicators = ['Q', 'M', '-', '/', 'quarter', 'month']
        if any(ind in col_str for ind in date_indicators):
            # Try to parse as date
            try:
                pd.to_datetime(col_str)
                return True
            except:
                pass
        
        return False
    
    def get_available_indicators(self) -> Dict[str, bool]:
        """
        Check which CSV files are available
        
        Returns:
            Dict of {indicator_id: file_exists}
        """
        
        availability = {}
        for indicator_id, filename in self.csv_mapping.items():
            filepath = os.path.join(self.csv_dir, filename)
            availability[indicator_id] = os.path.exists(filepath)
        
        return availability


# Test function
if __name__ == "__main__":
    loader = CSVDataLoader()
    
    print("\n" + "="*80)
    print("CSV DATA LOADER - Availability Check")
    print("="*80)
    
    availability = loader.get_available_indicators()
    
    available_count = sum(availability.values())
    total_count = len(availability)
    
    print(f"\nCSV Files Found: {available_count}/{total_count}\n")
    
    for indicator_id, is_available in availability.items():
        status = "[READY]" if is_available else "[MISSING]"
        filename = loader.csv_mapping[indicator_id]
        print(f"  {status} {indicator_id:25s} {filename}")
    
    print("\n" + "="*80)
    
    if available_count == 0:
        print("\n[WAITING] No CSV files found yet...")
        print("          Follow: eurozone_data/DOWNLOAD_CHECKLIST.txt")
    else:
        print(f"\n[SUCCESS] {available_count} files ready to integrate!")
        print("\nTesting available files:\n")
        
        for indicator_id, is_available in availability.items():
            if is_available:
                df = loader.load_series(indicator_id)
                if df is not None:
                    print(f"  [OK] {indicator_id}: {len(df)} observations")
    
    print("\n" + "="*80 + "\n")

