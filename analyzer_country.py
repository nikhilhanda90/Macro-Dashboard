"""
Country-Level Analysis for Eurozone Dashboard
Analyzes Germany and France as core engines of the Euro Area
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta


class CountryAnalyzer:
    """Analyzes country-level data and contributions to Euro Area aggregates"""
    
    # Country display names
    COUNTRY_NAMES = {
        "EA19": "Euro Area",
        "DE": "Germany",
        "FR": "France"
    }
    
    def __init__(self):
        pass
    
    def calculate_yoy_percentile(self, df: pd.DataFrame, lookback_years: int = 20) -> Optional[float]:
        """
        Calculate YoY growth and return its percentile ranking
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            lookback_years: Years of history for percentile calculation
            
        Returns:
            Percentile (0-100) of latest YoY growth, or None
        """
        if df is None or df.empty or len(df) < 13:
            return None
        
        try:
            df = df.sort_values('date').copy()
            
            # Calculate YoY change
            df['yoy'] = df['value'].pct_change(12) * 100  # Assumes monthly/quarterly
            
            # For quarterly data, use periods=4
            if len(df) < 50:  # Likely quarterly
                df['yoy'] = df['value'].pct_change(4) * 100
            
            # Get latest YoY
            latest_yoy = df['yoy'].iloc[-1]
            
            if pd.isna(latest_yoy):
                return None
            
            # Calculate percentile vs history
            cutoff_date = df['date'].max() - pd.DateOffset(years=lookback_years)
            historical = df[df['date'] >= cutoff_date]['yoy'].dropna()
            
            if len(historical) < 10:
                return None
            
            percentile = (historical < latest_yoy).sum() / len(historical) * 100
            
            return round(percentile, 1)
            
        except Exception as e:
            print(f"Error calculating YoY percentile: {e}")
            return None
    
    def calculate_level_percentile(self, df: pd.DataFrame, lookback_years: int = 20, inverted: bool = False) -> Optional[float]:
        """
        Calculate percentile of latest level value
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            lookback_years: Years of history for percentile calculation
            inverted: True for unemployment (lower is better)
            
        Returns:
            Percentile (0-100) of latest value, or None
        """
        if df is None or df.empty:
            return None
        
        try:
            df = df.sort_values('date').copy()
            
            # Get latest value
            latest_value = df['value'].iloc[-1]
            
            if pd.isna(latest_value):
                return None
            
            # Calculate percentile vs history
            cutoff_date = df['date'].max() - pd.DateOffset(years=lookback_years)
            historical = df[df['date'] >= cutoff_date]['value'].dropna()
            
            if len(historical) < 10:
                return None
            
            if inverted:
                # For unemployment: lower is better, so invert
                percentile = (historical > latest_value).sum() / len(historical) * 100
            else:
                percentile = (historical < latest_value).sum() / len(historical) * 100
            
            return round(percentile, 1)
            
        except Exception as e:
            print(f"Error calculating level percentile: {e}")
            return None
    
    def calculate_country_scores(
        self,
        country_data: Dict[str, Dict[str, Optional[pd.DataFrame]]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate growth, labor, and sentiment scores for each country
        With minimum data rules: need ≥2 indicators per category, ≥6 total to score
        
        Args:
            country_data: Nested dict {country: {indicator_name: DataFrame}}
            
        Returns:
            Dict {country: {'growth': score, 'labor': score, 'sentiment': score, 'macro_score': weighted, 'has_min_data': bool}}
        """
        scores = {}
        
        for country, indicators in country_data.items():
            growth_metrics = []
            labor_metrics = []
            sentiment_metrics = []
            
            # Growth indicators (YoY percentiles)
            for ind in ['Real GDP', 'Industrial Production', 'Retail Trade Volume', 'Construction Output']:
                if ind in indicators and indicators[ind] is not None:
                    pct = self.calculate_yoy_percentile(indicators[ind])
                    if pct is not None:
                        growth_metrics.append(pct)
            
            # Labor indicators
            if 'Unemployment Rate' in indicators and indicators['Unemployment Rate'] is not None:
                pct = self.calculate_level_percentile(indicators['Unemployment Rate'], inverted=True)
                if pct is not None:
                    labor_metrics.append(pct)
            
            if 'Employment Level' in indicators and indicators['Employment Level'] is not None:
                pct = self.calculate_yoy_percentile(indicators['Employment Level'])
                if pct is not None:
                    labor_metrics.append(pct)
            
            # Sentiment indicators (level percentiles)
            for ind in ['Economic Sentiment', 'Consumer Confidence']:
                if ind in indicators and indicators[ind] is not None:
                    pct = self.calculate_level_percentile(indicators[ind])
                    if pct is not None:
                        sentiment_metrics.append(pct)
            
            # Apply minimum data rules
            # Need at least 2 indicators per category to use that category
            growth_score = np.mean(growth_metrics) if len(growth_metrics) >= 2 else None
            labor_score = np.mean(labor_metrics) if len(labor_metrics) >= 2 else None
            sentiment_score = np.mean(sentiment_metrics) if len(sentiment_metrics) >= 2 else None
            
            # Count total indicators across all categories
            total_indicators = len(growth_metrics) + len(labor_metrics) + len(sentiment_metrics)
            has_min_data = total_indicators >= 6
            
            # Calculate macro score only if we have minimum data
            macro_score = None
            if has_min_data and any([growth_score, labor_score, sentiment_score]):
                # Weighted average of available scores
                weights = []
                values = []
                
                if growth_score is not None:
                    weights.append(0.5)
                    values.append(growth_score)
                if labor_score is not None:
                    weights.append(0.3)
                    values.append(labor_score)
                if sentiment_score is not None:
                    weights.append(0.2)
                    values.append(sentiment_score)
                
                if values:
                    total_weight = sum(weights)
                    macro_score = sum(w * v for w, v in zip(weights, values)) / total_weight
            
            scores[country] = {
                'growth': growth_score,
                'labor': labor_score,
                'sentiment': sentiment_score,
                'macro_score': macro_score,
                'n_growth': len(growth_metrics),
                'n_labor': len(labor_metrics),
                'n_sentiment': len(sentiment_metrics),
                'n_total': total_indicators,
                'has_min_data': has_min_data
            }
        
        return scores
    
    def calculate_contributions(
        self,
        indicator_name: str,
        country_data: Dict[str, Optional[pd.DataFrame]]
    ) -> Optional[pd.DataFrame]:
        """
        Calculate country contributions to Euro Area aggregate
        
        Args:
            indicator_name: Name of indicator (for weighting strategy)
            country_data: Dict {country_code: DataFrame with date/value}
            
        Returns:
            DataFrame with columns: date, EA_yoy, DE_contrib, FR_contrib, Rest_contrib
        """
        ea_df = country_data.get('EA19')
        de_df = country_data.get('DE')
        fr_df = country_data.get('FR')
        
        # Need at least EA and one country
        if ea_df is None or (de_df is None and fr_df is None):
            return None
        
        try:
            # Align dates (use EA dates as reference)
            ea_df = ea_df.sort_values('date').copy()
            
            # Calculate YoY for each
            freq = 12 if len(ea_df) > 50 else 4  # Monthly vs Quarterly
            ea_df['yoy'] = ea_df['value'].pct_change(freq) * 100
            
            result = ea_df[['date', 'yoy']].copy()
            result.columns = ['date', 'EA_yoy']
            
            # Get latest GDP levels for weighting
            ea_latest = ea_df['value'].iloc[-1]
            
            # Germany contribution
            if de_df is not None and not de_df.empty:
                de_df = de_df.sort_values('date').copy()
                de_df['yoy'] = de_df['value'].pct_change(freq) * 100
                
                # Merge on date
                result = result.merge(
                    de_df[['date', 'value', 'yoy']], 
                    on='date', 
                    how='left', 
                    suffixes=('', '_de')
                )
                
                # Calculate weight (GDP share)
                de_latest = de_df['value'].iloc[-1]
                w_de = de_latest / ea_latest if ea_latest > 0 else 0
                
                result['DE_contrib'] = result['yoy'] * w_de
            else:
                result['DE_contrib'] = 0
            
            # France contribution
            if fr_df is not None and not fr_df.empty:
                fr_df = fr_df.sort_values('date').copy()
                fr_df['yoy'] = fr_df['value'].pct_change(freq) * 100
                
                result = result.merge(
                    fr_df[['date', 'value', 'yoy']], 
                    on='date', 
                    how='left', 
                    suffixes=('', '_fr')
                )
                
                # Calculate weight
                fr_latest = fr_df['value'].iloc[-1]
                w_fr = fr_latest / ea_latest if ea_latest > 0 else 0
                
                result['FR_contrib'] = result['yoy'] * w_fr
            else:
                result['FR_contrib'] = 0
            
            # Rest of Euro Area (residual)
            result['Rest_contrib'] = result['EA_yoy'] - result['DE_contrib'] - result['FR_contrib']
            
            # Keep only complete rows
            result = result[['date', 'EA_yoy', 'DE_contrib', 'FR_contrib', 'Rest_contrib']].dropna()
            
            return result
            
        except Exception as e:
            print(f"Error calculating contributions: {e}")
            return None
    
    def get_score_color(self, score: Optional[float]) -> str:
        """
        Get color for score tile
        
        Args:
            score: Percentile score (0-100) or None
            
        Returns:
            Color code (hex)
        """
        if score is None:
            return '#808080'  # Gray
        elif score >= 60:
            return '#7cb342'  # Green
        elif score >= 40:
            return '#FFA500'  # Orange/Yellow
        else:
            return '#d32f2f'  # Red
    
    def get_score_label(self, score: Optional[float]) -> str:
        """Get text label for score"""
        if score is None:
            return "No Data"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Neutral"
        else:
            return "Weak"


def test_country_analyzer():
    """Test function"""
    print("Country Analyzer module loaded successfully")
    analyzer = CountryAnalyzer()
    print(f"Countries: {list(analyzer.COUNTRY_NAMES.values())}")


if __name__ == "__main__":
    test_country_analyzer()

