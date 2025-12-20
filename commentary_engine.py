"""
Nikhil's Take - Macro Commentary Engine
Generates data-driven high-level macro commentary from indicator aggregates
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class CommentaryEngine:
    """
    Generate intelligent macro commentary from cross-indicator analysis
    """
    
    # Cluster definitions
    CLUSTERS = {
        'Inflation & Rates': ['Fixed Income', 'Inflation'],
        'Growth & Demand': ['Growth'],
        'Labor & Wages': ['Labor'],
        'Credit & Risk': ['Credit', 'Market'],
        'Dollar & Liquidity': ['Fixed Income'],  # Dollar Index, SOFR, etc.
    }
    
    def aggregate_bucket_metrics(self, analysis_results: Dict, bucket: str, region: str = 'US') -> Dict:
        """
        Aggregate metrics for a bucket (Leading/Coincident/Lagging)
        
        Returns:
            {
                'avg_level': float (avg percentile_all),
                'avg_trend_z': float (avg trend_z),
                'n_indicators': int
            }
        """
        filtered = [
            v for v in analysis_results.values()
            if v and 
            v.get('region') == region and 
            v.get('indicator_type', '').lower() == bucket.lower()
        ]
        
        if not filtered:
            return {'avg_level': 50, 'avg_trend_z': 0, 'n_indicators': 0}
        
        levels = [v['percentile_all'] for v in filtered if v.get('percentile_all') is not None]
        trends = [v['trend_z'] for v in filtered if v.get('trend_z') is not None and not pd.isna(v['trend_z'])]
        
        return {
            'avg_level': np.mean(levels) if levels else 50,
            'avg_trend_z': np.mean(trends) if trends else 0,
            'n_indicators': len(filtered)
        }
    
    def aggregate_cluster_metrics(self, analysis_results: Dict, cluster_name: str, region: str = 'US') -> Dict:
        """
        Aggregate metrics for a cluster (Inflation & Rates, Growth & Demand, etc.)
        
        Returns:
            {
                'level_z': float (how high/low cluster is),
                'trend_z': float (cluster momentum)
            }
        """
        # First try direct cluster field, fallback to category mapping
        filtered = [
            v for v in analysis_results.values()
            if v and 
            v.get('region') == region and 
            v.get('cluster') == cluster_name
        ]
        
        # Fallback to category-based clustering if no cluster field
        if not filtered:
            cluster_categories = self.CLUSTERS.get(cluster_name, [])
            filtered = [
                v for v in analysis_results.values()
                if v and 
                v.get('region') == region and 
                v.get('category') in cluster_categories
            ]
        
        if not filtered:
            return {'level_z': 0, 'trend_z': 0}
        
        # Convert percentiles to Z-scores (approximate)
        levels = [v['percentile_all'] for v in filtered if v.get('percentile_all') is not None]
        level_z = (np.mean(levels) - 50) / 20 if levels else 0  # Rough Z-score
        
        trends = [v['trend_z'] for v in filtered if v.get('trend_z') is not None and not pd.isna(v['trend_z'])]
        trend_z = np.mean(trends) if trends else 0
        
        return {
            'level_z': level_z,
            'trend_z': trend_z
        }
    
    def cycle_momentum(self, lead_trend_z: float) -> str:
        """Describe cycle momentum based on leading indicators trend"""
        if lead_trend_z > 0.8:
            return "accelerating"
        elif lead_trend_z > 0.5:
            return "picking up"
        elif lead_trend_z < -0.8:
            return "rolling over hard"
        elif lead_trend_z < -0.5:
            return "slowing"
        else:
            return "flat"
    
    def cycle_stage(self, lead_level: float, lag_level: float) -> str:
        """
        Determine cycle stage from leading vs lagging levels
        
        High leading, low lagging = early expansion
        High leading, high lagging = late expansion / peak
        Low leading, high lagging = early contraction / cooling
        Low leading, low lagging = mid-contraction / trough
        """
        lead_high = lead_level > 55
        lead_low = lead_level < 45
        lag_high = lag_level > 55
        lag_low = lag_level < 45
        
        if lead_high and lag_low:
            return "early cycle"
        elif lead_high and lag_high:
            return "late cycle"
        elif lead_low and lag_high:
            return "turning down"
        elif lead_low and lag_low:
            return "late contraction"
        else:
            return "mid-cycle"
    
    def inflation_regime(self, inf_level_z: float, inf_trend_z: float) -> str:
        """Describe inflation & rates environment"""
        high = inf_level_z > 0.5
        low = inf_level_z < -0.5
        rising = inf_trend_z > 0.5
        falling = inf_trend_z < -0.5
        
        if high and rising:
            return "inflation's still elevated and building"
        elif high and falling:
            return "inflation's cooling from highs"
        elif high:
            return "inflation's above target"
        elif low and rising:
            return "inflation's picking up from lows"
        elif low and falling:
            return "deflation risk is building"
        elif low:
            return "inflation's below target"
        elif rising:
            return "inflation's drifting higher"
        elif falling:
            return "disinflation continues"
        else:
            return "inflation's anchored"
    
    def growth_labor_view(self, growth_trend_z: float, labor_trend_z: float) -> str:
        """Describe growth & labor momentum"""
        growth_strong = growth_trend_z > 0.5
        growth_weak = growth_trend_z < -0.5
        labor_strong = labor_trend_z > 0.5
        labor_weak = labor_trend_z < -0.5
        
        if growth_strong and labor_strong:
            return "growth and hiring both accelerating"
        elif growth_strong and labor_weak:
            return "growth picking up but labor softening"
        elif growth_weak and labor_strong:
            return "labor holding but growth slowing"
        elif growth_weak and labor_weak:
            return "both growth and labor weakening"
        elif growth_strong:
            return "activity accelerating"
        elif growth_weak:
            return "growth slowing"
        elif labor_strong:
            return "hiring strengthening"
        elif labor_weak:
            return "labor market cooling"
        else:
            return "growth and labor flat"
    
    def financial_conditions_view(
        self, 
        credit_level_z: float, 
        credit_trend_z: float, 
        dollar_trend_z: float,
        realrate_level: float
    ) -> str:
        """Describe financial conditions (credit, dollar, rates)"""
        credit_stress = credit_level_z > 0.5
        credit_easy = credit_level_z < -0.5
        credit_tightening = credit_trend_z > 0.5
        credit_easing = credit_trend_z < -0.5
        
        dollar_rising = dollar_trend_z > 0.5
        dollar_falling = dollar_trend_z < -0.5
        
        rates_high = realrate_level and realrate_level > 60
        rates_low = realrate_level and realrate_level < 40
        
        parts = []
        
        # Credit
        if credit_stress and credit_tightening:
            parts.append("credit tightening sharply")
        elif credit_stress:
            parts.append("spreads elevated")
        elif credit_easy and credit_easing:
            parts.append("credit flowing freely")
        elif credit_easing:
            parts.append("credit easing")
        elif credit_tightening:
            parts.append("credit tightening")
        else:
            parts.append("credit stable")
        
        # Dollar
        if dollar_rising:
            parts.append("dollar strengthening")
        elif dollar_falling:
            parts.append("dollar weakening")
        
        # Real rates
        if rates_high:
            if not parts:
                parts.append("real rates restrictive")
            else:
                parts[-1] += " (real rates restrictive)"
        elif rates_low:
            if not parts:
                parts.append("real rates accommodative")
            else:
                parts[-1] += " (real rates low)"
        
        if not parts:
            return "financial conditions are neutral"
        
        return ", ".join(parts) if len(parts) > 1 else parts[0]
    
    def us_macro_comment(
        self,
        stage: str,
        momentum: str,
        inflation_text: str,
        growth_labor_text: str,
        fincond_text: str
    ) -> str:
        """Build final commentary paragraph - narrative style like Nikhil's actual writing"""
        
        # Opening: paint the picture with metaphor
        if "early cycle" in stage.lower() and "picking up" in momentum:
            opening = "US macro is coming to life — leading indicators picking up steam, "
            signal_desc = "sentiment improving, credit behaving, and forward curves pricing growth"
            growth_bridge = "Growth and labor are both accelerating"
            implication = " The setup here typically supports risk assets if the momentum holds."
            watch = " Watch credit spreads and hours worked: any widening or softening is your first warning sign."
            
        elif "early cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "US macro is in early-cycle territory but the forward momentum stalled out — "
            signal_desc = "leading signals are mixed, with some green shoots but nothing convincing yet"
            growth_bridge = f"{growth_labor_text.capitalize()}, not giving much directional conviction"
            implication = " This chop can persist for a while before resolving."
            watch = " Watch the leading bucket: that's where the turn lives."
            
        elif "mid-cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "US macro is stuck in the middle lane — nothing strong enough to re-accelerate, nothing weak enough to break. "
            signal_desc = "Leading signals are a wash: sentiment is soft in places, credit spreads are calm, and rates markets aren't screaming either way"
            growth_bridge = f"{growth_labor_text.capitalize()}, not giving bears much to work with"
            implication = f" {inflation_text.capitalize()}, and real rates remain restrictive — policy is still the only thing pressing the brakes."
            watch = " If something cracks, it shows up first in credit or housing. Watch the leading bucket: that's where the turn lives."
            
        elif "late cycle" in stage.lower():
            opening = "US macro looks late cycle — "
            signal_desc = "leading indicators are elevated but showing signs of rolling over"
            growth_bridge = f"{growth_labor_text.capitalize()}, which is typical of late-expansion dynamics"
            implication = f" {inflation_text.capitalize()}, keeping policy tight."
            watch = " Watch labor and credit closely: that's where the cracks show up first in a downturn."
            
        elif "turning down" in stage.lower() or "rolling" in momentum.lower():
            opening = "US macro is rolling over — "
            signal_desc = "forward-looking indicators losing momentum across the board"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, but the Fed won't ease until they see real labor weakness."
            watch = " Watch for coincident indicators to follow. If they roll too, recession risk rises materially."
            
        else:
            # Fallback
            opening = f"US macro is {stage}, with leading indicators {momentum}. "
            signal_desc = f"{growth_labor_text}"
            growth_bridge = f"{inflation_text.capitalize()}"
            implication = f" {fincond_text.capitalize()}."
            watch = " Watch leading indicators for any shift in momentum."
        
        # Construct the narrative
        if "mid-cycle" in stage.lower() and "flat" in momentum.lower():
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{watch}"
        else:
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{watch}"
    
    def generate_us_commentary(self, analysis_results: Dict) -> str:
        """
        Generate full US macro commentary from analysis results
        
        Args:
            analysis_results: Dict from dashboard's load_all_data()
        
        Returns:
            Commentary paragraph string
        """
        # 1. Aggregate bucket metrics
        lead = self.aggregate_bucket_metrics(analysis_results, 'Leading', 'US')
        co = self.aggregate_bucket_metrics(analysis_results, 'Coincident', 'US')
        lag = self.aggregate_bucket_metrics(analysis_results, 'Lagging', 'US')
        
        # 2. Aggregate cluster metrics
        inflation_cluster = self.aggregate_cluster_metrics(analysis_results, 'Inflation & Rates', 'US')
        growth_cluster = self.aggregate_cluster_metrics(analysis_results, 'Growth & Demand', 'US')
        labor_cluster = self.aggregate_cluster_metrics(analysis_results, 'Labor & Wages', 'US')
        credit_cluster = self.aggregate_cluster_metrics(analysis_results, 'Credit & Risk', 'US')
        
        # Get real rate level (DFII10)
        realrate_pct = None
        for k, v in analysis_results.items():
            if k == 'DFII10' and v and v.get('region') == 'US':
                realrate_pct = v.get('percentile_all')
                break
        
        # 3. Generate text components
        stage = self.cycle_stage(lead['avg_level'], lag['avg_level'])
        momentum = self.cycle_momentum(lead['avg_trend_z'])
        inflation_text = self.inflation_regime(inflation_cluster['level_z'], inflation_cluster['trend_z'])
        growth_labor_text = self.growth_labor_view(growth_cluster['trend_z'], labor_cluster['trend_z'])
        fincond_text = self.financial_conditions_view(
            credit_cluster['level_z'],
            credit_cluster['trend_z'],
            0,  # Dollar trend (would need to extract from DTWEXBGS)
            realrate_pct
        )
        
        # 4. Build final commentary
        commentary = self.us_macro_comment(
            stage,
            momentum,
            inflation_text,
            growth_labor_text,
            fincond_text
        )
        
        return commentary
    
    def generate_eurozone_commentary(self, analysis_results: Dict) -> str:
        """
        Generate Eurozone macro commentary from analysis results
        
        Args:
            analysis_results: Dict from dashboard's load_all_data()
        
        Returns:
            Commentary paragraph string
        """
        # Same structure as US but for Eurozone region
        lead = self.aggregate_bucket_metrics(analysis_results, 'Leading', 'Eurozone')
        co = self.aggregate_bucket_metrics(analysis_results, 'Coincident', 'Eurozone')
        lag = self.aggregate_bucket_metrics(analysis_results, 'Lagging', 'Eurozone')
        
        inflation_cluster = self.aggregate_cluster_metrics(analysis_results, 'Inflation & Rates', 'Eurozone')
        growth_cluster = self.aggregate_cluster_metrics(analysis_results, 'Growth & Demand', 'Eurozone')
        labor_cluster = self.aggregate_cluster_metrics(analysis_results, 'Labor & Wages', 'Eurozone')
        credit_cluster = self.aggregate_cluster_metrics(analysis_results, 'Credit & Risk', 'Eurozone')
        
        # Get ECB deposit rate level
        ecb_rate_pct = None
        for k, v in analysis_results.items():
            if k == 'ECBDFR' and v and v.get('region') == 'Eurozone':
                ecb_rate_pct = v.get('percentile_all')
                break
        
        stage = self.cycle_stage(lead['avg_level'], lag['avg_level'])
        momentum = self.cycle_momentum(lead['avg_trend_z'])
        inflation_text = self.inflation_regime(inflation_cluster['level_z'], inflation_cluster['trend_z'])
        growth_labor_text = self.growth_labor_view(growth_cluster['trend_z'], labor_cluster['trend_z'])
        fincond_text = self.financial_conditions_view(
            credit_cluster['level_z'],
            credit_cluster['trend_z'],
            0,  # Euro doesn't have simple dollar equivalent
            ecb_rate_pct
        )
        
        # Build Eurozone-specific commentary - narrative style
        
        if "early cycle" in stage.lower() and "picking up" in momentum:
            opening = "Eurozone macro is showing some life — leading indicators picking up, "
            signal_desc = "sentiment improving off the lows, credit stable, and forward expectations turning constructive"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, giving the ECB some breathing room."
            watch = " Watch German manufacturing and peripheral spreads: those are your early warning indicators."
            
        elif "early cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "Eurozone macro is in early territory but momentum hasn't materialized yet — "
            signal_desc = "leading signals are mixed, with pockets of strength but no clear acceleration"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}."
            watch = " Watch the leading bucket closely: any directional move here matters for the EUR growth outlook."
            
        elif "mid-cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "Eurozone macro is stuck in neutral — nothing breaking down, nothing accelerating either. "
            signal_desc = "Leading signals are choppy: confidence surveys soft, credit markets calm, rates pricing in gradual normalization"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, and the ECB is holding policy tight — monetary restraint is still the dominant force."
            watch = " If cracks emerge, watch periphery spreads and core manufacturing. That's where stress shows up first."
            
        elif "late cycle" in stage.lower():
            opening = "Eurozone macro looks extended — "
            signal_desc = "leading indicators elevated but starting to soften"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, keeping ECB policy tight."
            watch = " Watch labor markets and peripheral sovereign spreads: those are the first dominoes if this rolls over."
            
        elif "turning down" in stage.lower() or "rolling" in momentum.lower():
            opening = "Eurozone macro is losing momentum — "
            signal_desc = "forward-looking indicators rolling over, sentiment deteriorating"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, but the ECB won't ease until core inflation cooperates."
            watch = " Watch for this weakness to spread from periphery to core. If Germany stalls, the whole bloc follows."
            
        else:
            opening = f"Eurozone macro is {stage}, with leading indicators {momentum}. "
            signal_desc = f"{growth_labor_text}"
            growth_bridge = f"{inflation_text.capitalize()}"
            implication = f" {fincond_text.capitalize()}."
            watch = " Watch leading indicators for any directional shift."
        
        if "mid-cycle" in stage.lower() and "flat" in momentum.lower():
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{watch}"
        else:
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{watch}"

    def generate_uk_commentary(self, analysis_results: Dict) -> str:
        """
        Generate UK macro commentary from analysis results
        
        Args:
            analysis_results: Dict from dashboard's load_all_data()
        
        Returns:
            Commentary paragraph string
        """
        # Same structure as US/Eurozone but for UK region
        lead = self.aggregate_bucket_metrics(analysis_results, 'Leading', 'UK')
        co = self.aggregate_bucket_metrics(analysis_results, 'Coincident', 'UK')
        lag = self.aggregate_bucket_metrics(analysis_results, 'Lagging', 'UK')
        
        inflation_cluster = self.aggregate_cluster_metrics(analysis_results, 'Inflation & Rates', 'UK')
        growth_cluster = self.aggregate_cluster_metrics(analysis_results, 'Growth & Demand', 'UK')
        labor_cluster = self.aggregate_cluster_metrics(analysis_results, 'Labor & Wages', 'UK')
        credit_cluster = self.aggregate_cluster_metrics(analysis_results, 'Credit & Risk', 'UK')
        
        # Get BoE Bank Rate level
        boe_rate_pct = None
        for k, v in analysis_results.items():
            if k == 'GBPONTD156N' and v and v.get('region') == 'UK':
                boe_rate_pct = v.get('percentile_all')
                break
        
        stage = self.cycle_stage(lead['avg_level'], lag['avg_level'])
        momentum = self.cycle_momentum(lead['avg_trend_z'])
        inflation_text = self.inflation_regime(inflation_cluster['level_z'], inflation_cluster['trend_z'])
        growth_labor_text = self.growth_labor_view(growth_cluster['trend_z'], labor_cluster['trend_z'])
        fincond_text = self.financial_conditions_view(
            credit_cluster['level_z'],
            credit_cluster['trend_z'],
            0,  # Sterling doesn't map to dollar index
            boe_rate_pct
        )
        
        # Build UK-specific commentary - narrative style (post-Brexit context)
        
        if "early cycle" in stage.lower() and "picking up" in momentum:
            opening = "UK macro is turning a corner — leading signals are firming, "
            signal_desc = "confidence ticking up, housing showing signs of life, and forward-looking indicators off the lows"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, which gives the BoE room to maneuver."
            watch = " Watch property prices and services inflation: those are where the BoE stress points live."
            
        elif "early cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "UK macro is stuck in the early stages but hasn't found traction yet — "
            signal_desc = "leading indicators are mixed, with pockets of improvement but no clear momentum"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, leaving the BoE in wait-and-see mode."
            watch = " Watch gilt yields and wage growth: those will dictate how restrictive policy really feels."
            
        elif "mid cycle" in stage.lower() and "picking up" in momentum:
            opening = "UK macro is in the expansion lane — leaders are pushing higher, "
            signal_desc = "business confidence strengthening, credit conditions easing, and growth expectations improving"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, which could force the BoE's hand sooner than expected."
            watch = " Watch services CPI and wage settlements: those are the BoE's red lines."
            
        elif "mid cycle" in stage.lower() and "flat" in momentum.lower():
            opening = "UK macro is grinding through mid-cycle — "
            signal_desc = "nothing strong enough to re-accelerate, nothing weak enough to break. Leading signals are stable but uninspiring"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, keeping the BoE anchored to restrictive policy."
            watch = " If something cracks, it shows up first in housing or consumer confidence. Watch the leading bucket closely."
            
        elif "late cycle" in stage.lower():
            opening = "UK macro is in late-cycle territory — leaders are high but momentum is fading, "
            signal_desc = "sentiment softening, financial conditions still tight, and forward indicators rolling over"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}. This is textbook late cycle — growth cooling while costs lag."
            watch = " Watch unemployment and retail sales: those are the first dominoes if the cycle turns."
            
        else:  # Contraction or ambiguous
            opening = "UK macro is softening — leading signals are pressing lower, "
            signal_desc = "confidence deteriorating, credit spreads widening, and forward-looking data weakening"
            growth_bridge = f"{growth_labor_text.capitalize()}"
            implication = f" {inflation_text.capitalize()}, which gives the BoE some cover to ease if needed."
            watch = " Watch labor market data and mortgage lending: those will signal whether this is a soft patch or something worse."
        
        # Add financial conditions overlay
        if "tight" in fincond_text.lower():
            fincond_bridge = f" {fincond_text.capitalize()}, which is still acting as a drag on activity."
        elif "neutral" in fincond_text.lower():
            fincond_bridge = f" {fincond_text.capitalize()}, neither helping nor hurting."
        else:
            fincond_bridge = f" {fincond_text.capitalize()}, providing tailwind to growth."
        
        # Combine into final narrative
        if "early" in stage.lower() or "contraction" in stage.lower():
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{fincond_bridge}{watch}"
        else:
            return f"{opening}{signal_desc}. {growth_bridge}.{implication}{watch}"


# Test function
if __name__ == "__main__":
    print("Commentary Engine - Test Mode")
    print("="*80)
    
    # Create mock data for testing
    mock_results = {
        'T10Y3M': {
            'region': 'US',
            'indicator_type': 'Leading',
            'category': 'Fixed Income',
            'percentile_all': 65,
            'trend_z': 0.8
        },
        'UNRATE': {
            'region': 'US',
            'indicator_type': 'Lagging',
            'category': 'Labor',
            'percentile_all': 45,
            'trend_z': -0.3
        },
        'DFII10': {
            'region': 'US',
            'indicator_type': 'Leading',
            'category': 'Fixed Income',
            'percentile_all': 75,
            'trend_z': 0.5
        }
    }
    
    engine = CommentaryEngine()
    commentary = engine.generate_us_commentary(mock_results)
    
    print("\nGenerated Commentary:")
    print(commentary)
    print("\n" + "="*80)

