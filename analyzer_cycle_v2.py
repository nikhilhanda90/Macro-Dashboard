"""
Economic Analyzer Module for Cycle Dashboard - V2
Uses indicator_config.py and trend_engine.py for enhanced trend analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import config_cycle_v2 as config
from indicator_config import (
    get_config_df, get_narrative, get_fun_line,
    dynamic_interpretation, trend_explainer
)
from trend_engine import TrendEngine


class CycleAnalyzerV2:
    """Analyzes economic data with proper trend interpretation"""
    
    def __init__(self):
        self.extreme_high = config.EXTREME_HIGH
        self.high = config.HIGH
        self.low = config.LOW
        self.extreme_low = config.EXTREME_LOW
        self.recent_years = config.RECENT_YEARS
        self.config_df = get_config_df()
        self.trend_engine = TrendEngine()
    
    def get_indicator_config(self, series_id: str) -> Optional[Dict]:
        """Get config for a specific indicator from new config table"""
        config_row = self.config_df[self.config_df['series_id'] == series_id]
        if config_row.empty:
            return None
        return config_row.iloc[0].to_dict()
    
    def get_indicator_config_from_old(self, series_id: str, old_config: Dict) -> Optional[Dict]:
        """
        Convert old config structure to new config structure
        This enables backward compatibility with config_cycle_v2.py
        """
        if not old_config:
            return None
        
        # Try to find in new config first
        new_config = self.get_indicator_config(series_id)
        if new_config:
            return new_config
        
        # Fallback: create pseudo-config from old structure
        # Map old indicator_type to new bucket
        indicator_type = old_config.get('indicator_type', 'Leading')
        bucket = indicator_type.lower()  # Leading -> leading
        
        # Infer trend_method from flags
        if old_config.get('use_yoy', False):
            trend_method = 'yoy'
        elif old_config.get('use_monthly_change', False):
            trend_method = 'mom'
        else:
            trend_method = 'level'
        
        # Infer type_tag from category/name
        category = old_config.get('category', '').lower()
        name = old_config.get('name', '').lower()
        
        # Simple heuristic mapping
        if 'inflation' in name or 'cpi' in name or 'pce' in name:
            type_tag = 'inflation'
        elif 'yield' in name or 'curve' in name:
            type_tag = 'yield_curve_slope' if 'curve' in name else 'policy_rate'
        elif 'spread' in name:
            type_tag = 'credit_spread'
        elif 'rate' in name and 'real' in name:
            type_tag = 'real_rate'
        elif 'sentiment' in name or 'confidence' in name:
            type_tag = 'sentiment'
        elif 'pmi' in name or 'production' in name or 'sales' in name:
            type_tag = 'growth_activity'
        elif 'payroll' in name or 'hours' in name:
            type_tag = 'labor_quantity'
        elif 'unemployment' in name:
            type_tag = 'labor_slack'
        elif 'wage' in name or 'cost' in name:
            type_tag = 'wages_costs'
        elif 'housing' in name or 'houst' in name:
            type_tag = 'housing_activity'
        elif 'mortgage' in name:
            type_tag = 'mortgage_rate'
        elif 'lending' in name:
            type_tag = 'lending_standards'
        elif 'vix' in name or 'vol' in name:
            type_tag = 'volatility_risk_off'
        elif 'dollar' in name:
            type_tag = 'fx_index'
        else:
            type_tag = 'growth_activity'  # default
        
        return {
            'series_id': series_id,
            'name': old_config.get('name', series_id),
            'bucket': bucket,
            'category': old_config.get('category', 'Unknown'),
            'frequency': old_config.get('frequency', 'monthly'),
            'use_yoy': old_config.get('use_yoy', False),
            'use_mom': old_config.get('use_monthly_change', False),
            'inverted': old_config.get('inverted', False),
            'type_tag': type_tag,
            'trend_method': trend_method,
            'region': old_config.get('region', 'US')
        }
    
    def calculate_percentile(self, df, current_value=None, years_back=None, inverted=False):
        """
        Calculate the percentile rank of the current value
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            current_value: Value to rank (if None, uses latest value)
            years_back: Only use data from last N years (None = all history)
            inverted: If True, flip percentile (high value = bad, e.g. VIX, unemployment)
            
        Returns:
            Percentile rank (0-100) or None
        """
        if df is None or df.empty:
            return None
        
        # Filter by date if years_back specified
        if years_back is not None:
            cutoff_date = datetime.now() - timedelta(days=365*years_back)
            df = df[df['date'] >= cutoff_date].copy()
        
        if df.empty:
            return None
        
        if current_value is None:
            current_value = df['value'].iloc[-1]
        
        values = df['value'].dropna()
        
        if len(values) < 10:
            return None
        
        percentile = (values < current_value).sum() / len(values) * 100
        
        # For inverted indicators (VIX, unemployment), flip the percentile
        # High value should = low percentile (bad)
        if inverted:
            percentile = 100 - percentile
        
        return round(percentile, 1)
    
    def get_display_value_and_unit(
        self, 
        df: pd.DataFrame, 
        series_id: str, 
        ind_config: Dict
    ) -> tuple:
        """
        Get the display value and unit based on indicator config
        
        Args:
            df: DataFrame with time series data
            series_id: Series identifier
            ind_config: Indicator configuration dict
        
        Returns:
            (display_value, unit, df_for_analysis)
        """
        df_sorted = df.sort_values('date').copy()
        
        trend_method = ind_config.get('trend_method', 'level')
        type_tag = ind_config.get('type_tag', '')
        
        # For inflation indicators using yoy, display the YoY change
        if trend_method == 'yoy' and 'inflation' in type_tag:
            # Determine YoY periods based on frequency
            frequency = ind_config.get('frequency', 'monthly').lower()
            if frequency == 'quarterly':
                yoy_periods = 4  # 4 quarters = 1 year
                min_length = 5
            elif frequency == 'monthly':
                yoy_periods = 12  # 12 months = 1 year
                min_length = 13
            else:
                # For daily/weekly
                yoy_periods = 252 if frequency == 'daily' else 52
                min_length = yoy_periods + 1
            
            if len(df_sorted) < min_length:
                return None, None, None
            
            df_sorted['yoy_change'] = df_sorted['value'].pct_change(periods=yoy_periods) * 100
            df_analysis = df_sorted.dropna(subset=['yoy_change']).copy()
            
            if df_analysis.empty:
                return None, None, None
            
            display_value = df_analysis['yoy_change'].iloc[-1]
            unit = '% YoY'
            
            # Return the YoY series for percentile calculations
            df_for_analysis = pd.DataFrame({
                'date': df_analysis['date'],
                'value': df_analysis['yoy_change']
            })
            
            return display_value, unit, df_for_analysis
        
        # For other yoy indicators (like Retail Sales, PCE)
        elif trend_method == 'yoy':
            # Determine YoY periods based on frequency
            frequency = ind_config.get('frequency', 'monthly').lower()
            if frequency == 'quarterly':
                yoy_periods = 4  # 4 quarters = 1 year
                min_length = 5
            elif frequency == 'monthly':
                yoy_periods = 12  # 12 months = 1 year
                min_length = 13
            else:
                # For daily/weekly, use approximation (252 trading days or 52 weeks)
                yoy_periods = 252 if frequency == 'daily' else 52
                min_length = yoy_periods + 1
            
            if len(df_sorted) < min_length:
                return None, None, None
            
            df_sorted['yoy_change'] = df_sorted['value'].pct_change(periods=yoy_periods) * 100
            df_analysis = df_sorted.dropna(subset=['yoy_change']).copy()
            
            if df_analysis.empty:
                return None, None, None
            
            display_value = df_analysis['yoy_change'].iloc[-1]
            unit = '% YoY'
            
            df_for_analysis = pd.DataFrame({
                'date': df_analysis['date'],
                'value': df_analysis['yoy_change']
            })
            
            return display_value, unit, df_for_analysis
        
        # For mom indicators (like Payrolls)
        elif trend_method == 'mom':
            if len(df_sorted) < 2:
                return None, None, None
            
            df_sorted['mom_change'] = df_sorted['value'].diff(1)
            df_analysis = df_sorted.dropna(subset=['mom_change']).copy()
            
            if df_analysis.empty:
                return None, None, None
            
            display_value = df_analysis['mom_change'].iloc[-1]
            unit = 'k jobs' if series_id == 'PAYEMS' else 'MoM'
            
            df_for_analysis = pd.DataFrame({
                'date': df_analysis['date'],
                'value': df_analysis['mom_change']
            })
            
            return display_value, unit, df_for_analysis
        
        # For level indicators (most common)
        else:
            display_value = df_sorted['value'].iloc[-1]
            
            # Infer unit from indicator type
            name = ind_config.get('name', '')
            name_lower = name.lower()
            
            if 'rate' in name_lower or 'yield' in name_lower or 'spread' in name_lower:
                unit = '%'
            elif 'index' in name_lower:
                unit = 'index'
            elif display_value > 1000:
                unit = 'level'
            else:
                unit = '%'
            
            df_for_analysis = df_sorted[['date', 'value']].copy()
            
            return display_value, unit, df_for_analysis
    
    def analyze_indicator(
        self, 
        df: pd.DataFrame, 
        series_id: str = None,
        name: str = None,
        region: str = 'US',
        old_config: Dict = None,  # NEW: Accept old config structure
        **kwargs  # For backward compatibility with old calls
    ) -> Optional[Dict]:
        """
        Perform comprehensive analysis using new config and trend engine
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            series_id: Series identifier (e.g., 'T10YIEM')
            name: Indicator name
            region: Region (default 'US')
            old_config: Old config dict from config_cycle_v2.py (for backward compatibility)
            **kwargs: Legacy parameters (ignored)
            
        Returns:
            Dictionary with analysis results including trend_comment
        """
        if df is None or df.empty:
            return None
        
        # Get config for this indicator
        try:
            if old_config:
                # Use old config and convert it
                ind_config = self.get_indicator_config_from_old(series_id, old_config)
                if ind_config is None:
                    raise ValueError(f"get_indicator_config_from_old returned None for {series_id}")
            else:
                # Try new config
                ind_config = self.get_indicator_config(series_id)
        except Exception as e:
            print(f"[ERROR in analyze_indicator - config] {series_id}: {e}")
            raise
        
        if ind_config is None:
            # Fallback to legacy behavior if no config found
            print(f"[Analyzer] Warning: No config found for {series_id}, using legacy analysis")
            return self._legacy_analyze(df, name, **kwargs)
        
        # Get display value and unit
        result = self.get_display_value_and_unit(df, series_id, ind_config)
        
        if result[0] is None:
            return None
        
        display_value, unit, df_for_analysis = result
        
        # Get current date
        current_date = df.sort_values('date')['date'].iloc[-1]
        
        # Calculate percentiles using the appropriate data
        is_inverted = ind_config.get('inverted', False)
        percentile_all = self.calculate_percentile(df_for_analysis, inverted=is_inverted)
        percentile_recent = self.calculate_percentile(df_for_analysis, years_back=self.recent_years, inverted=is_inverted)
        
        # Get trend analysis using TrendEngine
        df_for_trend = df.copy()
        df_for_trend['series_id'] = series_id
        df_for_trend['region'] = region
        
        trend_info = self.trend_engine.get_latest_trend(df_for_trend, series_id, region)
        
        if trend_info is None:
            trend_info = {
                'trend_z': None,
                'trend_label': 'Trend unavailable',
                'trend_comment': 'Insufficient data for trend analysis.'
            }
        
        # Get hover narrative and fun line
        narrative = get_narrative(series_id)
        fun_line = get_fun_line(series_id)
        
        # Generate dynamic interpretation and trend explainer
        trend_label_val = trend_info.get('trend_label', 'Flat →')
        type_tag_val = ind_config.get('type_tag', '')
        dynamic_line = dynamic_interpretation(trend_label_val, percentile_all, type_tag_val)
        explainer = trend_explainer(trend_label_val)
        
        # Build analysis result
        analysis = {
            'current_value': round(display_value, 2),
            'current_date': current_date,
            'percentile_all': percentile_all,
            'percentile_recent': percentile_recent,
            'trend_z': trend_info.get('trend_z'),
            'trend_label': trend_label_val,
            'trend_comment': trend_info.get('trend_comment', ''),  # Old verbose comment
            'trend_explainer': explainer,  # NEW: 6-month momentum explainer
            'dynamic_line': dynamic_line,  # NEW: Dynamic interpretation
            'indicator_type': ind_config.get('bucket', '').title(),  # leading -> Leading
            'category': ind_config.get('category', 'Unknown'),
            'cluster': ind_config.get('cluster', None),  # NEW: Cluster assignment
            'type_tag': type_tag_val,
            'unit': unit,
            'data': df_for_analysis,  # Use transformed data for charting (YoY, MoM, etc.)
            'inverted': ind_config.get('inverted', False),
            'narrative': narrative,  # Detailed narrative for hover
            'fun_line': fun_line,  # NEW: Catchy one-liner
            'series_id': series_id,
            'name': name,
            'region': region,
            'hidden': ind_config.get('hidden', False),  # Pass through hidden flag
            'contextual': ind_config.get('contextual', False)  # Pass through contextual flag (excluded from scoring)
        }
        
        return analysis
    
    def _legacy_analyze(self, df, name, **kwargs):
        """Fallback to legacy analysis for indicators without config"""
        # Simplified legacy logic
        current_value = df['value'].iloc[-1]
        current_date = df['date'].iloc[-1]
        
        is_inverted = kwargs.get('inverted', False)
        percentile_all = self.calculate_percentile(df, inverted=is_inverted)
        percentile_recent = self.calculate_percentile(df, years_back=self.recent_years, inverted=is_inverted)
        
        return {
            'current_value': round(current_value, 2),
            'current_date': current_date,
            'percentile_all': percentile_all,
            'percentile_recent': percentile_recent,
            'trend_label': 'N/A',
            'trend_comment': 'Legacy indicator - no trend analysis available.',
            'indicator_type': kwargs.get('indicator_type', 'Unknown'),
            'unit': '%',
            'data': df,
            'inverted': kwargs.get('inverted', False),
            'narrative': 'No description available.'
        }
    
    def calculate_cycle_summary(self, analysis_results: Dict, indicator_type: str) -> Dict:
        """
        Calculate summary for a group of indicators (Leading/Coincident/Lagging)
        
        Args:
            analysis_results: Dictionary of analysis results
            indicator_type: 'Leading', 'Coincident', or 'Lagging'
            
        Returns:
            dict with 'label', 'color', 'avg_percentile'
        """
        # Filter indicators of this type
        type_indicators = [
            result for result in analysis_results.values()
            if result and result.get('indicator_type', '').lower() == indicator_type.lower()
        ]
        
        if not type_indicators:
            return {
                'label': 'No data', 
                'color': config.SUMMARY_COLORS['neutral'], 
                'avg_percentile': None
            }
        
        # Calculate average percentile (using all-time percentile)
        percentiles = [
            ind['percentile_all'] for ind in type_indicators 
            if ind.get('percentile_all') is not None
        ]
        
        if not percentiles:
            return {
                'label': 'Insufficient data', 
                'color': config.SUMMARY_COLORS['neutral'], 
                'avg_percentile': None
            }
        
        avg_percentile = sum(percentiles) / len(percentiles)
        
        # Classify as Weak / Neutral / Strong
        if avg_percentile >= 65:
            label = "Strong"
            color = config.SUMMARY_COLORS['strong']
        elif avg_percentile <= 35:
            label = "Weak"
            color = config.SUMMARY_COLORS['weak']
        else:
            label = "Neutral"
            color = config.SUMMARY_COLORS['neutral']
        
        return {
            'label': label,
            'color': color,
            'avg_percentile': round(avg_percentile, 1)
        }


# Test function
if __name__ == "__main__":
    print("\n" + "="*80)
    print("Cycle Analyzer V2 - Test Mode")
    print("="*80)
    
    # Create synthetic test data
    dates = pd.date_range('2020-01-01', '2024-12-01', freq='M')
    test_df = pd.DataFrame({
        'date': dates,
        'value': np.linspace(1.5, 2.5, len(dates)) + np.random.randn(len(dates)) * 0.1
    })
    
    analyzer = CycleAnalyzerV2()
    result = analyzer.analyze_indicator(test_df, 'T10YIEM', '10Y Breakeven Inflation', 'US')
    
    if result:
        print(f"\n{result['name']}")
        print(f"  Current Value: {result['current_value']}{result['unit']}")
        print(f"  Date: {result['current_date']}")
        print(f"  Percentiles: All-time {result['percentile_all']}%, Recent {result['percentile_recent']}%")
        print(f"  Trend: {result['trend_label']} (Z={result['trend_z']:.2f})")
        print(f"  Interpretation: {result['trend_comment']}")
        print(f"  Narrative: {result['narrative'][:100]}...")
    
    print("\n" + "="*80 + "\n")

