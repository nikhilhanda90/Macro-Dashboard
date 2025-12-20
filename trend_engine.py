"""
Trend Engine - Computes trend_z and trend_label with economic interpretation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from indicator_config import get_config_df, get_interpretation, trend_direction


class TrendEngine:
    """
    Computes trend signals and interpretations for macro indicators
    
    Methodology:
    1. Join config metadata to raw time series
    2. Compute trend_base using trend_method (level/yoy/mom)
    3. Compute trend_z (standardized score)
    4. Generate trend_label (Strong up/Mild up/Flat/Mild down/Strong down)
    5. Generate trend_comment (plain-English interpretation)
    """
    
    def __init__(self):
        self.config_df = get_config_df()
    
    def get_frequency_shift(self, frequency: str, periods: int = 1) -> int:
        """
        Convert frequency and periods to number of rows to shift
        
        Args:
            frequency: 'daily', 'weekly', 'monthly', 'quarterly'
            periods: Number of periods (e.g., 1 year)
        
        Returns:
            Number of rows to shift (approximation)
        """
        freq_map = {
            'daily': 252,      # Trading days per year
            'weekly': 52,      # Weeks per year
            'monthly': 12,     # Months per year
            'quarterly': 4,    # Quarters per year
            'annual': 1        # Years per year
        }
        return freq_map.get(frequency, 12) * periods
    
    def compute_trend_base(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        Compute trend_base for a single (series_id, region) group
        
        Args:
            group: DataFrame with columns [date, value, trend_method, frequency]
        
        Returns:
            DataFrame with added column: trend_base
        """
        g = group.sort_values('date').copy()
        
        if len(g) < 2:
            g['trend_base'] = np.nan
            return g
        
        method = g['trend_method'].iloc[0]
        frequency = g['frequency'].iloc[0]
        
        # Get 1-year shift for this frequency
        year_shift = self.get_frequency_shift(frequency, periods=1)
        
        if method == "yoy":
            # YoY % change
            g['value_1y_ago'] = g['value'].shift(year_shift)
            g['trend_base'] = (g['value'] / g['value_1y_ago']) - 1.0
        
        elif method == "mom":
            # Month-over-month change (or period-over-period)
            g['trend_base'] = g['value'].diff(1)
        
        elif method == "level":
            # 6-month change in level (better for momentum tracking)
            half_year_shift = year_shift // 2  # 6 months
            g['value_6m_ago'] = g['value'].shift(half_year_shift)
            g['trend_base'] = g['value'] - g['value_6m_ago']
        
        else:
            g['trend_base'] = np.nan
        
        return g
    
    def compute_trend_z_and_label(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        Compute trend_z and trend_label for a single group
        
        Args:
            group: DataFrame with trend_base column
        
        Returns:
            DataFrame with added columns: trend_z, trend_label
        """
        g = group.sort_values('date').copy()
        base = g['trend_base']
        
        # Require sufficient history
        if base.count() < 12:
            g['trend_z'] = np.nan
            g['trend_label'] = "Trend unavailable"
            return g
        
        # Compute Z-score
        mean = base.mean()
        std = base.std(ddof=0)
        
        if std > 0 and not np.isnan(std):
            g['trend_z'] = (base - mean) / std
        else:
            g['trend_z'] = np.nan
        
        # Map Z-score to label
        def label_from_z(z):
            if pd.isna(z):
                return "Trend unavailable"
            if z > 1.0:
                return "Strong up ↑↑"
            if z > 0.3:
                return "Mild up ↑"
            if z < -1.0:
                return "Strong down ↓↓"
            if z < -0.3:
                return "Mild down ↓"
            return "Flat →"
        
        g['trend_label'] = g['trend_z'].apply(label_from_z)
        
        return g
    
    def build_trend_comment(self, row: pd.Series) -> str:
        """
        Generate plain-English interpretation of trend
        
        Args:
            row: DataFrame row with trend_label and type_tag
        
        Returns:
            Interpretation string
        """
        dir_ = trend_direction(row['trend_label'])
        type_ = row.get('type_tag', 'unknown')
        return get_interpretation(type_, dir_)
    
    def process_time_series(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Full pipeline: compute trend_base, trend_z, trend_label, trend_comment
        
        Args:
            df_raw: DataFrame with columns [series_id, region, date, value]
        
        Returns:
            Enhanced DataFrame with trend columns
        """
        # Join config (drop region from config to avoid conflict)
        config_no_region = self.config_df.drop(columns=['region'], errors='ignore')
        df = df_raw.merge(config_no_region, on='series_id', how='left')
        
        # Check for missing config
        missing = df[df['type_tag'].isna()]['series_id'].unique()
        if len(missing) > 0:
            print(f"[TrendEngine] Warning: No config found for: {missing}")
        
        # Compute trend_base
        df = df.groupby(['series_id', 'region'], group_keys=False).apply(
            self.compute_trend_base
        )
        
        # Compute trend_z and label
        df = df.groupby(['series_id', 'region'], group_keys=False).apply(
            self.compute_trend_z_and_label
        )
        
        # Generate trend comment
        df['trend_comment'] = df.apply(self.build_trend_comment, axis=1)
        
        return df
    
    def get_latest_trend(
        self, 
        df_raw: pd.DataFrame, 
        series_id: str, 
        region: str = 'US'
    ) -> Optional[Dict]:
        """
        Get latest trend info for a single indicator
        
        Args:
            df_raw: Raw time series data
            series_id: Series identifier
            region: Region (default 'US')
        
        Returns:
            Dict with trend_z, trend_label, trend_comment, or None
        """
        # Filter to this indicator
        indicator_df = df_raw[
            (df_raw['series_id'] == series_id) & 
            (df_raw['region'] == region)
        ].copy()
        
        if indicator_df.empty:
            return None
        
        # Process
        processed = self.process_time_series(indicator_df)
        
        # Get latest row
        latest = processed.sort_values('date').iloc[-1]
        
        return {
            'trend_z': latest.get('trend_z'),
            'trend_label': latest.get('trend_label'),
            'trend_comment': latest.get('trend_comment'),
            'trend_base': latest.get('trend_base'),
            'date': latest.get('date')
        }


def analyze_indicator_trend(
    time_series: pd.DataFrame,
    series_id: str,
    region: str = 'US'
) -> Dict:
    """
    Convenience function to analyze a single indicator's trend
    
    Args:
        time_series: DataFrame with columns [date, value]
        series_id: Series identifier
        region: Region
    
    Returns:
        Dict with trend analysis
    """
    # Prepare dataframe
    df = time_series.copy()
    df['series_id'] = series_id
    df['region'] = region
    
    # Compute trend
    engine = TrendEngine()
    result = engine.get_latest_trend(df, series_id, region)
    
    return result


# Test function
if __name__ == "__main__":
    print("\n" + "="*80)
    print("Trend Engine - Test Mode")
    print("="*80)
    
    # Create synthetic data for testing
    dates = pd.date_range('2020-01-01', '2024-12-01', freq='M')
    
    # Test case 1: Rising trend
    test_data_1 = pd.DataFrame({
        'series_id': 'T10YIEM',
        'region': 'US',
        'date': dates,
        'value': np.linspace(1.5, 2.5, len(dates)) + np.random.randn(len(dates)) * 0.1
    })
    
    engine = TrendEngine()
    result_1 = engine.get_latest_trend(test_data_1, 'T10YIEM', 'US')
    
    print("\nTest 1: Rising 10Y Breakeven")
    print(f"  Trend Z-score: {result_1['trend_z']:.2f}")
    print(f"  Trend Label: {result_1['trend_label']}")
    print(f"  Interpretation: {result_1['trend_comment']}")
    
    # Test case 2: Falling trend
    test_data_2 = pd.DataFrame({
        'series_id': 'UNRATE',
        'region': 'US',
        'date': dates,
        'value': np.linspace(6.0, 4.0, len(dates)) + np.random.randn(len(dates)) * 0.1
    })
    
    result_2 = engine.get_latest_trend(test_data_2, 'UNRATE', 'US')
    
    print("\nTest 2: Falling Unemployment")
    print(f"  Trend Z-score: {result_2['trend_z']:.2f}")
    print(f"  Trend Label: {result_2['trend_label']}")
    print(f"  Interpretation: {result_2['trend_comment']}")
    
    print("\n" + "="*80 + "\n")

