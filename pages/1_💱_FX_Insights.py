"""
FX Insights - EURUSD Analysis
Nikhil's comprehensive FX view with Valuation, Technicals, and Positioning
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="FX Insights - Nikhil Dashboard",
    page_icon="💱",
    layout="wide"
)

# =====================================================================
# TECHNICAL INDICATOR EXPLAINERS
# =====================================================================
def get_rsi_explainer(rsi_value):
    """Generate dynamic RSI explainer"""
    if rsi_value > 70:
        state = "momentum is strong but stretched"
    elif rsi_value >= 50:
        state = "momentum is positive"
    elif rsi_value >= 30:
        state = "momentum is weakening"
    else:
        state = "momentum is deeply oversold"
    return f"Measures momentum strength; {state}."

def get_macd_explainer(macd_hist, macd_hist_prev):
    """Generate dynamic MACD explainer"""
    if macd_hist > macd_hist_prev:
        state = "momentum is building"
    elif macd_hist < macd_hist_prev:
        state = "momentum is fading"
    else:
        state = "momentum lacks conviction"
    return f"Tracks trend momentum; {state}."

def get_bb_explainer(bb_width_pct):
    """Generate dynamic Bollinger Width explainer"""
    if bb_width_pct < 20:
        state = "market is coiled, breakout risk rising"
    elif bb_width_pct <= 80:
        state = "volatility is normal"
    else:
        state = "volatility elevated, trend maturing"
    return f"Measures volatility; {state}."

def get_atr_explainer(atr_pct):
    """Generate dynamic ATR explainer"""
    if atr_pct > 70:
        state = "volatility is high, exhaustion risk present"
    elif atr_pct >= 30:
        state = "volatility is moderate"
    else:
        state = "volatility is compressed, coiled for a move"
    return f"Measures price volatility; {state}."

# =====================================================================
# TECHNICAL LEVELS COMMENTARY GENERATOR
# =====================================================================
def get_technical_levels_commentary(context):
    """
    Generate dynamic commentary explaining how current price interacts with key levels.
    
    Args:
        context: dict with:
            - spot: float
            - trend_state: str ('bullish', 'neutral', 'bearish')
            - confirmation_status: str ('confirmed', 'not_confirmed')
            - key_levels: list of dicts with 'name', 'price', 'type', 'distance_pct'
    
    Returns:
        str - 2 sentences max explaining price vs levels
    """
    spot = context.get('spot', 0)
    trend_state = context.get('trend_state', 'neutral')
    confirmation_status = context.get('confirmation_status', 'not_confirmed')
    key_levels = context.get('key_levels', [])
    
    if not key_levels:
        return "Price action is unclear without established key levels."
    
    # Separate supports and resistances
    supports = sorted([l for l in key_levels if l['type'] == 'Support'], key=lambda x: abs(x['distance_pct']))
    resistances = sorted([l for l in key_levels if l['type'] == 'Resistance'], key=lambda x: abs(x['distance_pct']))
    
    nearest_support = supports[0] if supports else None
    nearest_resistance = resistances[0] if resistances else None
    
    # Find major levels (200d MA, 1Y high/low)
    major_trend_level = next((l for l in key_levels if '200d MA' in l['name']), None)
    major_breakout = next((l for l in key_levels if '1-year High' in l['name'] or '1-year Low' in l['name']), None)
    
    # Generate commentary based on context
    if trend_state == 'bullish':
        # Check if above major MA cluster
        if major_trend_level and spot > major_trend_level['price']:
            if nearest_resistance and abs(nearest_resistance['distance_pct']) < 2:
                # Near resistance
                support_text = f"{nearest_support['name']}" if nearest_support else "support"
                return f"Price is testing resistance at {nearest_resistance['name']} ({nearest_resistance['price']:.4f}). A break confirms momentum; failure likely leads to consolidation toward {support_text}."
            else:
                # Holding above support
                if nearest_resistance:
                    return f"Price is holding above key moving-average support, keeping the medium-term trend intact. Upside momentum requires a break above {nearest_resistance['name']} ({nearest_resistance['price']:.4f})."
                else:
                    return f"Price is holding above key moving-average support, keeping the medium-term trend intact."
        elif major_trend_level:
            # Below major MA but still bullish score
            support_text = f"{nearest_support['name']}" if nearest_support else "lower support"
            return f"Price is consolidating below {major_trend_level['name']} ({major_trend_level['price']:.4f}). A reclaim confirms bullish structure; failure shifts focus toward {support_text}."
        else:
            # No major level found
            return f"Price is in bullish territory but lacks clear structural reference points. Watch for breakout confirmation."
    
    elif trend_state == 'bearish':
        # Bearish regime
        if major_trend_level and spot < major_trend_level['price']:
            if nearest_support and abs(nearest_support['distance_pct']) < 2:
                # Near support
                resistance_text = f"{nearest_resistance['name']}" if nearest_resistance else "resistance"
                return f"Price is testing support at {nearest_support['name']} ({nearest_support['price']:.4f}). A break extends downside; defense likely leads to consolidation toward {resistance_text}."
            else:
                # Below major MA
                if nearest_support:
                    return f"Price is trading below key moving-average resistance, maintaining bearish structure. Further downside targets {nearest_support['name']} ({nearest_support['price']:.4f})."
                else:
                    return f"Price is trading below key moving-average resistance, maintaining bearish structure."
        elif major_trend_level:
            # Above major MA but bearish score
            return f"Price is holding above {major_trend_level['name']} ({major_trend_level['price']:.4f}) despite bearish signals. A breakdown confirms; holding suggests consolidation."
        else:
            # No major level found
            return f"Price is in bearish territory but lacks clear structural reference points. Watch for breakdown confirmation."
    
    else:  # Neutral
        # Range conditions
        if nearest_support and nearest_resistance:
            support_dist = abs(nearest_support['distance_pct'])
            resistance_dist = abs(nearest_resistance['distance_pct'])
            
            if support_dist < 1 and resistance_dist < 1:
                # Tight range
                return f"Price is trapped between {nearest_support['name']} ({nearest_support['price']:.4f}) and {nearest_resistance['name']} ({nearest_resistance['price']:.4f}). A breakout in either direction likely signals the next move."
            elif support_dist < resistance_dist:
                # Closer to support
                return f"Price is consolidating near {nearest_support['name']} ({nearest_support['price']:.4f}). A break lower extends downside; a rebound targets {nearest_resistance['name']}."
            else:
                # Closer to resistance
                return f"Price is consolidating near {nearest_resistance['name']} ({nearest_resistance['price']:.4f}). A break higher extends upside; a rejection targets {nearest_support['name']}."
        else:
            return "Price is in a neutral range. Watch for breakout confirmation at key levels."

# =====================================================================
# VALUATION MEANING GENERATOR
# =====================================================================
def get_valuation_meaning(signal_key, context):
    """
    Generate dynamic 'What it means' text for Valuation Snapshot.
    
    Args:
        signal_key: str - One of: 'macro_fv', 'mispricing_trend', 'weekly_pressure', 'decision_regime'
        context: dict - Contains:
            - fv_z: float (e.g., +1.32)
            - fv_state: str ('rich', 'cheap', 'fair')
            - fv_strength: str ('mild', 'moderate', 'strong')
            - mispricing_trend: str ('widening', 'stabilizing', 'compressing')
            - weekly_pressure: str ('compressing', 'expanding', 'neutral')
            - decision_regime: str ('fade_rallies', 'buy_dips', 'momentum_up', etc.)
            - confidence: str ('low', 'medium', 'high') [optional]
    
    Returns:
        str - One decision-relevant sentence, max 18 words
    """
    # Extract context
    fv_z = context.get('fv_z', 0)
    fv_state = context.get('fv_state', 'fair')
    fv_strength = context.get('fv_strength', 'mild')
    mispricing_trend = context.get('mispricing_trend', 'stabilizing')
    weekly_pressure = context.get('weekly_pressure', 'neutral')
    decision_regime = context.get('decision_regime', 'neutral')
    confidence = context.get('confidence', 'medium')
    
    # Strength modifiers
    strength_map = {
        'mild': 'slightly',
        'moderate': 'meaningfully',
        'strong': 'extremely'
    }
    strength_modifier = strength_map.get(fv_strength, '')
    
    # ===== ROW 1: MACRO FAIR VALUE =====
    if signal_key == 'macro_fv':
        if fv_state == 'rich':
            return f"EUR is {strength_modifier} above macro fair value; upside needs improving fundamentals."
        elif fv_state == 'cheap':
            return f"EUR is {strength_modifier} below macro fair value; downside needs worsening fundamentals."
        else:  # fair
            return "EUR is near macro fair value; fundamentals don't argue for a strong trend."
    
    # ===== ROW 2: MISPRICING TREND =====
    elif signal_key == 'mispricing_trend':
        base_text = {
            'widening': "Valuation gap is widening; momentum can persist despite fundamentals.",
            'stabilizing': "Valuation gap is stabilizing; momentum is fading.",
            'compressing': "Valuation gap is closing; mean reversion pressure is rising."
        }
        return base_text.get(mispricing_trend, "Mispricing trend unclear; monitor for direction.")
    
    # ===== ROW 3: WEEKLY PRESSURE =====
    elif signal_key == 'weekly_pressure':
        # Cross-signal consistency: check if rich + expanding OR cheap + compressing
        if fv_state == 'rich' and weekly_pressure == 'expanding':
            return "Near-term upside flow, but rich valuation limits reward; fade rallies tactically."
        elif fv_state == 'cheap' and weekly_pressure == 'compressing':
            return "Near-term downside flow; cheap can get cheaper, wait for stabilization."
        
        # Standard logic
        base_text = {
            'compressing': "Near-term downside pressure; rallies may struggle without a catalyst.",
            'expanding': "Near-term upside pressure; dips may attract buyers.",
            'neutral': "Balanced near-term flow; wait for confirmation before positioning."
        }
        return base_text.get(weekly_pressure, "Weekly pressure unclear; monitor flow dynamics.")
    
    # ===== ROW 4: DECISION REGIME =====
    elif signal_key == 'decision_regime':
        # Add "mispricing can persist" clause if widening
        persistence_clause = " Mispricing can persist." if mispricing_trend == 'widening' else ""
        
        regime_text = {
            'fade_rallies': f"Fade rallies; risk-reward favors mean reversion over chasing.{persistence_clause}",
            'mean_reversion': f"Mean reversion setup; fade extremes, don't chase trends.{persistence_clause}",
            'buy_dips': f"Buy dips; risk-reward favors mean reversion higher.{persistence_clause}",
            'momentum_up': "Trend-following; breakouts are more likely to hold.",
            'momentum_down': "Trend-following; breakdowns are more likely to extend.",
            'neutral': "Stay tactical; signals are mixed and range risk is high."
        }
        
        return regime_text.get(decision_regime, "Regime unclear; await stronger signal alignment.")
    
    return "Signal interpretation not available."

def derive_valuation_context(summary):
    """
    Derive context dict from FX Views summary data.
    
    Args:
        summary: dict from fx_views_summary.json
    
    Returns:
        dict with fv_z, fv_state, fv_strength, mispricing_trend, weekly_pressure, decision_regime
    """
    context = {}
    
    # Extract fv_z from summary
    fv_z = summary.get('mispricing_z', 0)
    context['fv_z'] = fv_z
    
    # Derive fv_state and fv_strength
    abs_z = abs(fv_z)
    if abs_z < 0.5:
        context['fv_state'] = 'fair'
        context['fv_strength'] = 'mild'
    elif abs_z < 1.0:
        context['fv_state'] = 'rich' if fv_z > 0 else 'cheap'
        context['fv_strength'] = 'mild'
    elif abs_z < 1.5:
        context['fv_state'] = 'rich' if fv_z > 0 else 'cheap'
        context['fv_strength'] = 'moderate'
    else:
        context['fv_state'] = 'rich' if fv_z > 0 else 'cheap'
        context['fv_strength'] = 'strong'
    
    # Extract mispricing trend (you may need to compute this from historical data)
    # For now, derive from summary if available
    regime = summary.get('regime', 'In-line')
    if 'Break' in regime:
        context['mispricing_trend'] = 'widening'
    elif 'Stretch' in regime:
        context['mispricing_trend'] = 'stabilizing'
    else:
        context['mispricing_trend'] = 'compressing'
    
    # Extract weekly pressure
    pressure = summary.get('pressure_direction', 'neutral')
    if 'compress' in pressure.lower():
        context['weekly_pressure'] = 'compressing'
    elif 'expand' in pressure.lower():
        context['weekly_pressure'] = 'expanding'
    else:
        context['weekly_pressure'] = 'neutral'
    
    # Extract decision regime
    stance = summary.get('stance', 'neutral')
    if 'fade' in stance.lower() or 'overvaluation' in stance.lower():
        context['decision_regime'] = 'fade_rallies'
    elif 'dip' in stance.lower() or 'attractive' in stance.lower():
        context['decision_regime'] = 'buy_dips'
    elif 'momentum' in stance.lower() and 'value' in stance.lower():
        context['decision_regime'] = 'momentum_up'
    elif 'trend' in stance.lower():
        context['decision_regime'] = 'momentum_up'
    else:
        context['decision_regime'] = 'mean_reversion' if abs_z > 1.0 else 'neutral'
    
    return context

# =====================================================================
# MODERN DARK THEME CSS
# =====================================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(to bottom, #1a1f2e 0%, #0f1419 100%);
    }
    
    .main {
        background: transparent;
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Premium title */
    .fx-title {
        font-size: 3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .fx-subtitle {
        font-size: 1.3rem;
        color: #00A676;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Nikhil Commentary Box (Top) */
    .nikhil-commentary {
        background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%);
        border: 2px solid #00A676;
        border-radius: 16px;
        padding: 2.5rem;
        margin: 2rem 0 3rem 0;
        box-shadow: 0 0 30px rgba(0, 166, 118, 0.3);
    }
    
    .commentary-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00A676;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .commentary-text {
        font-size: 1.15rem;
        color: #e0e0e0;
        line-height: 1.8;
        font-weight: 400;
    }
    
    /* Card Sections */
    .insight-card {
        background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%);
        border: 1px solid #3a4254;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        border-color: #00A676;
        box-shadow: 0 0 25px rgba(0, 166, 118, 0.2);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #00A676;
    }
    
    /* Nikhil's View Section (Bottom of each card) */
    .nikhil-view {
        background: rgba(0, 166, 118, 0.1);
        border-left: 4px solid #00A676;
        border-radius: 8px;
        padding: 1.25rem;
        margin-top: 1.5rem;
    }
    
    .view-header {
        font-size: 0.95rem;
        color: #00A676;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    
    .view-text {
        font-size: 1.05rem;
        color: #e0e0e0;
        line-height: 1.6;
        font-style: italic;
    }
    
    /* Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00A676, transparent);
        margin: 2.5rem 0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        padding: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%);
        border: 2px solid #3a4254;
        border-radius: 12px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 1rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #00A676;
        box-shadow: 0 0 20px rgba(0, 166, 118, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00A676 0%, #008C5E 100%) !important;
        border-color: #00A676 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 25px rgba(0, 166, 118, 0.4);
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# Load Data Functions
# =====================================================================

@st.cache_data(ttl=3600)
def load_fx_views_decision():
    """Load FX Views decision table output"""
    try:
        decision_path = Path(__file__).parent.parent / 'FX Views' / '5_outputs' / 'eurusd_fx_views_decision.json'
        with open(decision_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Decision table not available: {e}")
        return None

@st.cache_data(ttl=3600)
def load_fx_views_charts():
    """Load FX Views chart paths"""
    base_path = Path(__file__).parent.parent / 'FX Views' / '5_outputs'
    charts = {
        'fair_value': base_path / 'eurusd_fxviews_fair_value_monthly.png',
        'mispricing': base_path / 'eurusd_fxviews_mispricing_z_monthly.png',
        'pressure': base_path / 'eurusd_fxviews_pressure_weekly.png',
        'decision_map': base_path / 'eurusd_fxviews_decision_map.png'
    }
    
    for key, path in charts.items():
        if not path.exists():
            return None
    
    return charts

@st.cache_data(ttl=3600)
def load_cftc_positioning():
    """Load CFTC positioning data"""
    try:
        positioning_path = Path(__file__).parent.parent / 'FX Views' / 'cftc_outputs' / 'cftc_positioning_summary.json'
        csv_path = Path(__file__).parent.parent / 'FX Views' / 'cftc_outputs' / 'cftc_eur_positioning.csv'
        
        with open(positioning_path, 'r') as f:
            summary = json.load(f)
        
        history = None
        if csv_path.exists():
            history = pd.read_csv(csv_path, parse_dates=['date'])
        
        return summary, history
    except Exception as e:
        return None, None

@st.cache_data(ttl=3600)
def load_technical_analysis():
    """Load technical analysis summary"""
    try:
        tech_path = Path(__file__).parent.parent / 'FX Views' / 'technical_outputs' / 'eurusd_technical_summary.json'
        with open(tech_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

# Load data
decision = load_fx_views_decision()
charts = load_fx_views_charts()
cftc_summary, cftc_history = load_cftc_positioning()
technical = load_technical_analysis()

# =====================================================================
# HEADER
# =====================================================================
st.markdown('<h1 class="fx-title">💱 FX Insights</h1>', unsafe_allow_html=True)
st.markdown('<p class="fx-subtitle">EURUSD • Valuation, Technicals & Positioning</p>', unsafe_allow_html=True)

# =====================================================================
# NIKHIL'S FX COMMENTARY (TOP - Synthesis)
# =====================================================================
st.markdown("""
<div class="nikhil-commentary">
    <div class="commentary-header">💬 Nikhil's FX Commentary</div>
    <div class="commentary-text">
        <p><strong>EUR is stuck in the middle lane</strong> — nothing strong enough to re-accelerate, nothing weak enough to break. 
        The macro fair value model says rich (+1.3σ), weekly pressure is compressing, and positioning sits neutral. 
        Not giving bears much to work with, but bulls lack conviction.</p>
        
        <p>Valuation points to mean reversion, technicals are mixed, and CFTC speculative positioning shows no crowding risk. 
        The framework suggests fading rallies rather than chasing them, but with limited urgency. 
        Watch for catalysts: if macro surprises turn negative or positioning shifts, downside asymmetry increases.</p>
        
        <p><strong>Bottom line:</strong> Overvaluation fading mode. Lean mean-revert, but wait for confirmation.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# HORIZONTAL TABS
# =====================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📈 VALUATION", "📊 TECHNICALS", "🎯 POSITIONING"])

# =====================================================================
# TAB 1: VALUATION
# =====================================================================
with tab1:
    if decision and charts:
        # ==================================================================
        # PLAIN ENGLISH TAKEAWAY — Above the Table
        # ==================================================================
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%); 
                    border-left: 4px solid #D4AF37; 
                    padding: 1.5rem 2rem; margin: 0 0 2rem 0; border-radius: 8px;">
            <div style="color: #D4AF37; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; 
                        letter-spacing: 0.08em; margin-bottom: 0.75rem;">Valuation Takeaway</div>
            <div style="color: #FFFFFF; font-size: 1.15rem; line-height: 1.75; font-weight: 400;">
                EUR looks expensive, but the risk of further overvaluation is fading. 
                Macro models show EUR trading above fair value. That mispricing is no longer worsening, 
                and short-term pressure is compressing. The setup favors fading rallies, not chasing downside 
                — unless a macro or policy shock shifts the regime.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ==================================================================
        # VALUATION SNAPSHOT — Signal Table
        # ==================================================================
        st.markdown("### 📊 Valuation Snapshot — EURUSD")
        
        # Decision data
        inputs = decision['inputs']
        stance = decision['stance']
        
        # Build dynamic context directly from inputs for intelligent "What it means"
        fv_z = inputs.get('z_val', 0)
        abs_z = abs(fv_z)
        
        # Derive fv_state and fv_strength
        if abs_z < 0.5:
            fv_state = 'fair'
            fv_strength = 'mild'
        elif abs_z < 1.0:
            fv_state = 'rich' if fv_z > 0 else 'cheap'
            fv_strength = 'mild'
        elif abs_z < 1.5:
            fv_state = 'rich' if fv_z > 0 else 'cheap'
            fv_strength = 'moderate'
        else:
            fv_state = 'rich' if fv_z > 0 else 'cheap'
            fv_strength = 'strong'
        
        # Derive mispricing trend from regime
        regime = inputs.get('val_bucket', 'FAIR')
        if 'BREAK' in regime:
            mispricing_trend = 'widening'
        elif 'STRETCH' in regime:
            mispricing_trend = 'stabilizing'
        else:
            mispricing_trend = 'compressing'
        
        # Extract pressure direction
        pressure_dir = inputs.get('pressure_dir', 'neutral')
        if 'compress' in pressure_dir.lower():
            weekly_pressure_read = 'Compressing'
            weekly_pressure = 'compressing'
        elif 'expand' in pressure_dir.lower():
            weekly_pressure_read = 'Expanding'
            weekly_pressure = 'expanding'
        else:
            weekly_pressure_read = 'Neutral'
            weekly_pressure = 'neutral'
        
        # Extract decision regime
        stance_title = stance.get('stance_title', 'Neutral')
        decision_regime = decision.get('action_bias', 'neutral').lower().replace('-', '_')
        
        # Build context dict for meaning generator
        context = {
            'fv_z': fv_z,
            'fv_state': fv_state,
            'fv_strength': fv_strength,
            'mispricing_trend': mispricing_trend,
            'weekly_pressure': weekly_pressure,
            'decision_regime': decision_regime
        }
        
        # Build dynamic verdict table
        snapshot_data = {
            'Signal': [
                'Macro Fair Value',
                'Mispricing Trend',
                'Weekly Pressure',
                'Decision Regime'
            ],
            'Read': [
                f"{inputs['z_val']:+.1f}σ {inputs['val_bucket'].replace('_', ' ').title()}",
                mispricing_trend.title(),
                weekly_pressure_read,
                stance_title
            ],
            'What it means': [
                get_valuation_meaning('macro_fv', context),
                get_valuation_meaning('mispricing_trend', context),
                get_valuation_meaning('weekly_pressure', context),
                get_valuation_meaning('decision_regime', context)
            ]
        }
        
        df_snapshot = pd.DataFrame(snapshot_data)
        
        # Display as clean table
        st.markdown("""
        <style>
        .snapshot-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0 2.5rem 0;
        }
        .snapshot-table th {
            background: #242b3d;
            color: #00A676;
            padding: 1rem;
            text-align: left;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid #00A676;
        }
        .snapshot-table td {
            padding: 0.85rem 1rem;
            border-bottom: 1px solid #3a4254;
            color: #e0e0e0;
        }
        .snapshot-table tr:hover {
            background: rgba(0, 166, 118, 0.05);
        }
        .read-col {
            color: #FFFFFF;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render table with HTML for better control
        table_html = '<table class="snapshot-table"><thead><tr>'
        for col in df_snapshot.columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        for _, row in df_snapshot.iterrows():
            table_html += '<tr>'
            table_html += f'<td>{row["Signal"]}</td>'
            table_html += f'<td class="read-col">{row["Read"]}</td>'
            table_html += f'<td>{row["What it means"]}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # ==================================================================
        # CHART STACK — Evidence
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📈 Why the Model Says It")
        
        # Chart 1: Macro Fair Value (Monthly)
        st.markdown("#### Macro Fair Value (Monthly)")
        st.markdown("<p style='color: #888888; font-size: 0.9rem; font-style: italic; margin-top: -0.5rem; margin-bottom: 1rem; opacity: 0.85;'>Compares EUR's spot price to the level implied by growth, rates, inflation, and risk differentials.</p>", unsafe_allow_html=True)
        st.image(str(charts['fair_value']), use_container_width=True)
        
        # Chart 2: Mispricing Z-Score (Time Series)
        st.markdown("#### Mispricing Z-Score (Time Series)")
        st.markdown("<p style='color: #888888; font-size: 0.9rem; font-style: italic; margin-top: -0.5rem; margin-bottom: 1rem; opacity: 0.85;'>Shows how far EUR is from fair value relative to its own history, measured in standard deviations.</p>", unsafe_allow_html=True)
        st.image(str(charts['mispricing']), use_container_width=True)
        
        # Chart 3: Weekly Pressure Panel
        st.markdown("#### Weekly Pressure Panel")
        st.markdown("<p style='color: #888888; font-size: 0.9rem; font-style: italic; margin-top: -0.5rem; margin-bottom: 1rem; opacity: 0.85;'>Tracks short-term flow and momentum signals to gauge whether buying or selling pressure is building.</p>", unsafe_allow_html=True)
        st.image(str(charts['pressure']), use_container_width=True)
        
        # Chart 4: Decision Map (Valuation × Pressure)
        st.markdown("#### Decision Map (Valuation × Pressure)")
        st.markdown("<p style='color: #888888; font-size: 0.9rem; font-style: italic; margin-top: -0.5rem; margin-bottom: 1rem; opacity: 0.85;'>Combines valuation and short-term pressure to indicate whether the setup favors mean reversion or momentum.</p>", unsafe_allow_html=True)
        st.image(str(charts['decision_map']), use_container_width=True)
        
        # ==================================================================
        # MODEL INTERPRETATION — Technical Depth (Bottom)
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1.5rem;">
            <div style="color: #888888; font-size: 0.85rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.75rem;">🔬 Model Interpretation</div>
            <div style="color: #d0d0d0; font-size: 0.95rem; line-height: 1.6;">
                <strong>Layer 1:</strong> ElasticNet macro valuation shows +1.3σ mispricing (spot above fair value).<br>
                <strong>Layer 2:</strong> Weekly pressure model indicates compression (mean reversion signal).<br>
                <strong>Historical analogues:</strong> Fading rallies outperforms trend-following in this regime. 
                Setup favors patience over aggressive positioning until valuation compresses or macro deteriorates.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning("Valuation data not available. Run FX Views generation script.")

# =====================================================================
# TAB 2: TECHNICALS
# =====================================================================
with tab2:
    if technical:
        score = technical['technical_score']
        structure_score = technical.get('structure_score', 0)
        momentum_score = technical.get('momentum_score', 0)
        vol_bonus = technical.get('vol_bonus', 0)
        confirmation_status = technical.get('confirmation_status', 'not_confirmed')
        risk_flags = technical.get('risk_flags', [])
        regime = technical['regime']
        indicators = technical.get('indicators', {})
        
        # ==================================================================
        # NIKHIL'S VIEW ON TECHNICALS — Commentary (TOP)
        # ==================================================================
        st.markdown(f"""
        <div style='background: rgba(0, 123, 255, 0.1); border-left: 4px solid #007BFF; 
                    padding: 1.5rem 2rem; margin: 0 0 2rem 0; border-radius: 8px;'>
            <div style='color: #007BFF; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; 
                        letter-spacing: 0.08em; margin-bottom: 0.75rem;'>💬 Nikhil's View on Technicals</div>
            <div style='color: #FFFFFF; font-size: 1.05rem; line-height: 1.7; font-weight: 400;'>
                EUR's technical setup is constructive but unconfirmed. Price holds above the 200-day moving average, 
                RSI is overbought, and momentum indicators show mixed follow-through. Volatility is compressed, 
                signaling a potential breakout ahead. Watch key resistance levels—confirmation requires a sustained 
                break with expanding volume. Until then, this is a wait-for-confirmation trade, not a chase.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ==================================================================
        # TECHNICALS SNAPSHOT — State Detection
        # ==================================================================
        st.markdown("### 📊 Technical Snapshot — EURUSD")
        
        # Determine trend signal
        spot = technical['spot']
        sma_200 = indicators.get('SMA_200', 0)
        trend_signal = "Above 200d MA" if spot > sma_200 else "Below 200d MA"
        trend_read = "Medium-term uptrend intact" if spot > sma_200 else "Medium-term downtrend"
        
        # Determine momentum label from NORMALIZED momentum_score (M_norm)
        M_norm_snapshot = momentum_score / 3.0  # Normalize for snapshot display
        if M_norm_snapshot > 0.33:
            momentum_signal = "Positive"
        elif M_norm_snapshot < -0.33:
            momentum_signal = "Negative"
        else:
            momentum_signal = "Mixed"
        
        # Add risk qualifier if present (risk flags are separate from momentum state)
        if "Overbought" in risk_flags:
            momentum_signal += " ⚠️"  # Visual flag, not part of momentum label
        elif "Oversold" in risk_flags:
            momentum_signal += " ⚠️"
        
        momentum_read = "Strong follow-through" if M_norm_snapshot > 0.5 else "No strong follow-through" if M_norm_snapshot > -0.5 else "Losing momentum"
        
        # Determine volatility signal
        percentiles = technical.get('percentiles', {})
        bb_width_pct = percentiles.get('bb_width_pct', 50)
        if bb_width_pct < 30:
            vol_signal = "Compressed"
            vol_read = "Break risk rising"
        elif bb_width_pct > 70:
            vol_signal = "Expanded"
            vol_read = "High volatility regime"
        else:
            vol_signal = "Normal"
            vol_read = "Range conditions"
        
        # Build technical snapshot
        tech_snapshot_data = {
            'Dimension': [
                'Trend',
                'Momentum',
                'Volatility',
                'Technical Regime'
            ],
            'Signal': [
                trend_signal,
                momentum_signal,
                vol_signal,
                regime
            ],
            'Read': [
                trend_read,
                momentum_read,
                vol_read,
                'Range → Break Setup' if regime == 'Neutral' else regime + ' bias'
            ]
        }
        
        df_tech_snapshot = pd.DataFrame(tech_snapshot_data)
        
        # Render technical snapshot table
        table_html = '<table class="snapshot-table"><thead><tr>'
        for col in df_tech_snapshot.columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        for _, row in df_tech_snapshot.iterrows():
            table_html += '<tr>'
            table_html += f'<td>{row["Dimension"]}</td>'
            table_html += f'<td class="read-col">{row["Signal"]}</td>'
            table_html += f'<td>{row["Read"]}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # ==================================================================
        # SCORE VISUALIZATION — Directional Bias
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Calculate NORMALIZED drivers (MUST match score calculation logic)
        S_norm = structure_score / 2.5  # Structure normalized to [-1, +1]
        M_norm = momentum_score / 3.0   # Momentum normalized to [-1, +1]
        
        # VALIDATION: Ensure drivers are consistent with score
        # If score is non-zero, at least one normalized driver must be non-zero
        if abs(score) > 0.1:  # Non-zero score
            if abs(S_norm) < 0.01 and abs(M_norm) < 0.01:  # Both drivers are zero
                st.error("⚠️ Technical Score Bug: Non-zero score with zero drivers. This is a data integrity issue.")
        
        # Determine score color and subtitle based on score AND confirmation
        score_color = '#00A676' if score > 0 else '#EF4444' if score < 0 else '#888888'
        
        # Dynamic subtitle - standardized confirmation phrases
        if score >= 1.5:
            subtitle = "Bullish, confirmed" if confirmation_status == "confirmed" else "Constructive, not confirmed"
        elif score <= -1.5:
            subtitle = "Bearish, confirmed" if confirmation_status == "confirmed" else "Bearish bias, watch confirmation"
        else:
            subtitle = "Range conditions"
        
        # Generate text-based drivers for clarity
        if abs(S_norm) > 0.6:
            structure_text = "strong" if S_norm > 0 else "weak"
        elif abs(S_norm) > 0.3:
            structure_text = "leaning bullish" if S_norm > 0 else "leaning bearish"
        else:
            structure_text = "neutral"
        
        if abs(M_norm) > 0.6:
            momentum_text = "supportive" if M_norm > 0 else "fading"
        elif abs(M_norm) > 0.3:
            momentum_text = "positive" if M_norm > 0 else "negative"
        else:
            momentum_text = "mixed"
        
        # Create a proper visual card with driver breakdown
        st.markdown(f"""
        <div style='max-width: 600px; margin: 2rem auto; text-align: center;'>
            <div style='color: #888888; font-size: 0.85rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 1rem;'>
                Technical Score
            </div>
            <div style='background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%); 
                        border: 2px solid {score_color}; border-radius: 16px; 
                        padding: 2rem; box-shadow: 0 0 20px {score_color}40;'>
                <div style='color: {score_color}; font-size: 4rem; font-weight: 700; 
                            font-family: "Courier New", monospace; text-shadow: 0 0 15px {score_color}60;'>
                    {score:+.1f}
                </div>
                <div style='color: #888888; font-size: 0.9rem; margin-top: 0.5rem;'>
                    Range: -3 to +3
                </div>
                <div style='color: #888888; font-size: 0.85rem; margin-top: 1rem; opacity: 0.8;'>
                    Drivers: Structure {structure_text}, Momentum {momentum_text} → Score {score:+.1f}
                </div>
            </div>
            <div style='color: #d0d0d0; font-size: 1.05rem; font-style: italic; margin-top: 1rem;'>
                {subtitle}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show risk flags if any
        if risk_flags:
            flags_pills = " ".join([f'<span style="background: rgba(255,68,68,0.2); color: #ff4444; padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.8rem; margin: 0 0.25rem;">{flag}</span>' for flag in risk_flags])
            st.markdown(f"""
            <div style='text-align: center; margin-top: 0.5rem; margin-bottom: 1rem;'>
                {flags_pills}
            </div>
            """, unsafe_allow_html=True)
        
        # Add "View changes if..." trigger line
        key_levels_list = technical.get('key_levels', [])
        if key_levels_list:
            # Find nearest resistance and support
            resistances = [l for l in key_levels_list if l['type'] == 'Resistance']
            supports = [l for l in key_levels_list if l['type'] == 'Support']
            
            nearest_resistance = min(resistances, key=lambda x: abs(x['distance_pct'])) if resistances else None
            nearest_support = min(supports, key=lambda x: abs(x['distance_pct'])) if supports else None
            
            if nearest_resistance and nearest_support:
                trigger_text = f"Score upgrades if break above {nearest_resistance['name']} ({nearest_resistance['price']:.4f}); downgrades if break below {nearest_support['name']} ({nearest_support['price']:.4f})."
            elif nearest_resistance:
                trigger_text = f"Score upgrades if break above {nearest_resistance['name']} ({nearest_resistance['price']:.4f})."
            elif nearest_support:
                trigger_text = f"Score downgrades if break below {nearest_support['name']} ({nearest_support['price']:.4f})."
            else:
                trigger_text = ""
            
            if trigger_text:
                st.markdown(f"""
                <div style='text-align: center; margin-top: 0.5rem; margin-bottom: 2rem;'>
                    <div style='color: #888888; font-size: 0.85rem; font-style: italic;'>
                        ⚡ {trigger_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ==================================================================
        # ONE PRICE CHART — Visual Truth
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📈 Price Chart")
        
        chart_path = Path(__file__).parent.parent / 'FX Views' / 'technical_outputs' / 'eurusd_technical_chart.html'
        if chart_path.exists():
            with open(chart_path, 'r', encoding='utf-8') as f:
                chart_html = f.read()
            components.html(chart_html, height=1000, scrolling=True)
        else:
            st.info("📊 **Candlestick chart available after running technical generator**")
        
        # ==================================================================
        # KEY LEVELS — Decision Triggers
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🎯 Key Levels — What Matters if Price Moves")
        
        levels = technical.get('key_levels', [])
        
        # Generate dynamic levels commentary
        if levels:
            # Determine trend_state from regime
            trend_state = regime.lower() if regime in ['Bullish', 'Bearish'] else 'neutral'
            
            levels_context = {
                'spot': spot,
                'trend_state': trend_state,
                'confirmation_status': confirmation_status,
                'key_levels': levels
            }
            
            levels_commentary = get_technical_levels_commentary(levels_context)
            
            st.markdown(f"""
            <div style='background: rgba(0, 123, 255, 0.1); border-left: 4px solid #007BFF; 
                        padding: 1.25rem; margin: 0 0 1.5rem 0; border-radius: 4px;'>
                <div style='color: #d0d0d0; font-size: 1rem; line-height: 1.7;'>
                    {levels_commentary}
                </div>
            </div>
            """, unsafe_allow_html=True)
        if levels:
            for level in levels[:5]:  # Top 5 only
                level_type_color = '#00A676' if level['type'] == 'Support' else '#EF4444'
                level_icon = '↑' if level['type'] == 'Resistance' else '↓'
                dist_sign = '+' if level['distance_pct'] > 0 else ''
                
                # Determine what it means
                if level['type'] == 'Resistance':
                    meaning = "Break = trend acceleration" if '200d' in level['name'] or 'High' in level['name'] else "Upside trigger"
                else:
                    meaning = "Trend line in sand" if '200d' in level['name'] else "Near-term support"
                
                st.markdown(f"""
                <div style="background: rgba(26, 31, 46, 0.5); border-left: 4px solid {level_type_color}; 
                            border-radius: 4px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <span style="color: #FFFFFF; font-family: 'Courier New', monospace; font-size: 1.15rem; font-weight: 700;">
                                {level['price']:.4f}
                            </span>
                            <span style="color: {level_type_color}; font-size: 0.9rem; margin-left: 0.75rem;">
                                {level_icon} {level['name']}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #888888; font-size: 0.85rem;">
                                {dist_sign}{level['distance_pct']:.2f}%
                            </div>
                            <div style="color: #d0d0d0; font-size: 0.9rem; font-style: italic;">
                                {meaning}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ==================================================================
        # INDICATOR CHECK — Confirmation
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ✓ Indicator Check")
        st.markdown('<p style="color: #888888; font-size: 0.9rem; margin-bottom: 1.5rem;">Confirmation / Divergence signals</p>', unsafe_allow_html=True)
        
        # Get indicator values
        rsi = indicators.get('RSI', 0)
        macd = indicators.get('MACD', 0)
        macd_hist = indicators.get('MACD', 0) - indicators.get('MACD_Signal', 0) if indicators.get('MACD_Signal') else 0
        macd_hist_prev = 0  # Would need to calculate from data
        bb_width_pct = technical['percentiles'].get('bb_width_pct', 0)
        atr_pct = technical['percentiles'].get('atr_pct', 0)
        
        # Generate dynamic explainers
        rsi_explainer = get_rsi_explainer(rsi)
        macd_explainer = get_macd_explainer(macd_hist, macd_hist_prev)
        bb_explainer = get_bb_explainer(bb_width_pct)
        atr_explainer = get_atr_explainer(atr_pct)
        
        # RSI Panel
        rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        rsi_color = "#ff4444" if rsi > 70 else "#00A676" if rsi < 30 else "#888888"
        
        st.markdown(f"""
        <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="color: #FFFFFF; font-weight: 700; font-size: 1rem;">RSI (14)</div>
                <div style="color: {rsi_color}; font-weight: 600; font-size: 1.1rem;">{rsi:.1f}</div>
            </div>
            <div style="color: #888888; font-size: 0.85rem; font-style: italic; margin-bottom: 0.5rem;">
                {rsi_explainer}
            </div>
            <div style="color: {rsi_color}; font-size: 0.9rem; font-weight: 600;">
                → {rsi_signal}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # MACD Panel
        macd_signal = "Positive momentum" if macd > 0 else "Negative momentum" if macd < 0 else "No thrust"
        macd_color = "#00A676" if macd > 0 else "#ff4444" if macd < 0 else "#888888"
        
        st.markdown(f"""
        <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="color: #FFFFFF; font-weight: 700; font-size: 1rem;">MACD</div>
                <div style="color: {macd_color}; font-weight: 600; font-size: 1.1rem;">{macd:.4f}</div>
            </div>
            <div style="color: #888888; font-size: 0.85rem; font-style: italic; margin-bottom: 0.5rem;">
                {macd_explainer}
            </div>
            <div style="color: {macd_color}; font-size: 0.9rem; font-weight: 600;">
                → {macd_signal}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bollinger Width Panel
        bb_signal = "Coiled" if bb_width_pct < 20 else "Expanding" if bb_width_pct > 70 else "Normal"
        bb_color = "#007BFF" if bb_width_pct < 20 else "#ff4444" if bb_width_pct > 80 else "#888888"
        
        st.markdown(f"""
        <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="color: #FFFFFF; font-weight: 700; font-size: 1rem;">Bollinger Width</div>
                <div style="color: {bb_color}; font-weight: 600; font-size: 1.1rem;">{bb_width_pct:.0f}%ile</div>
            </div>
            <div style="color: #888888; font-size: 0.85rem; font-style: italic; margin-bottom: 0.5rem;">
                {bb_explainer}
            </div>
            <div style="color: {bb_color}; font-size: 0.9rem; font-weight: 600;">
                → {bb_signal}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ATR Panel (optional but recommended)
        atr = indicators.get('ATR', 0)
        atr_signal = "Exhaustion risk" if atr_pct > 70 else "Coiled" if atr_pct < 30 else "Moderate"
        atr_color = "#ff4444" if atr_pct > 70 else "#007BFF" if atr_pct < 30 else "#888888"
        
        st.markdown(f"""
        <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="color: #FFFFFF; font-weight: 700; font-size: 1rem;">ATR (20)</div>
                <div style="color: {atr_color}; font-weight: 600; font-size: 1.1rem;">{atr:.4f} ({atr_pct:.0f}%ile)</div>
            </div>
            <div style="color: #888888; font-size: 0.85rem; font-style: italic; margin-bottom: 0.5rem;">
                {atr_explainer}
            </div>
            <div style="color: {atr_color}; font-size: 0.9rem; font-weight: 600;">
                → {atr_signal}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning("Technical analysis data not available. Run: `py eurusd_technicals.py`")

# =====================================================================
# TAB 3: POSITIONING
# =====================================================================
with tab3:
    
    if cftc_summary:
        # ==================================================================
        # POSITIONING SNAPSHOT — Risk Contribution
        # ==================================================================
        st.markdown("### 📊 Positioning Snapshot — EURUSD")
        
        # Build positioning snapshot
        z_score = cftc_summary['z_1y']
        net_pos = cftc_summary['net_position']
        state = cftc_summary['positioning_state']
        
        # Determine momentum (you can add delta logic here when available)
        momentum_signal = "Flat"  # Could be dynamic: "Building" / "Reducing"
        momentum_icon = "→"
        
        # Risk contribution logic
        if abs(z_score) < 1.0:
            risk_contrib = "Low"
            risk_read = "Not a driver"
        elif z_score > 1.5:
            risk_contrib = "High"
            risk_read = "Fragility rising"
        else:
            risk_contrib = "Moderate"
            risk_read = "Watch for acceleration"
        
        positioning_snapshot_data = {
            'Dimension': [
                'Spec Length',
                'Z-Score (1Y)',
                'Momentum',
                'Risk Contribution'
            ],
            'Read': [
                state.replace('_', ' ').title(),
                f"{z_score:+.2f}σ",
                f"{momentum_icon} {momentum_signal}",
                risk_contrib
            ],
            'Interpretation': [
                "Not crowded" if abs(z_score) < 1.0 else "Stretched" if abs(z_score) > 1.5 else "Elevated",
                "Neutral-to-light" if abs(z_score) < 1.0 else "Crowded",
                "No chase behavior" if momentum_signal == "Flat" else "Flows accelerating",
                risk_read
            ]
        }
        
        df_pos_snapshot = pd.DataFrame(positioning_snapshot_data)
        
        # Render positioning snapshot table
        table_html = '<table class="snapshot-table"><thead><tr>'
        for col in df_pos_snapshot.columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        for _, row in df_pos_snapshot.iterrows():
            table_html += '<tr>'
            table_html += f'<td>{row["Dimension"]}</td>'
            table_html += f'<td class="read-col">{row["Read"]}</td>'
            table_html += f'<td>{row["Interpretation"]}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # ==================================================================
        # FUNCTIONAL COMMENTARY — Not Neutral, But Low Constraint
        # ==================================================================
        st.markdown(f"""
        <div style="background: rgba(26, 31, 46, 0.5); border-left: 4px solid #9333EA; 
                    padding: 1.25rem; margin: 1.5rem 0; border-radius: 4px;">
            <div style="color: #d0d0d0; font-size: 1rem; line-height: 1.7;">
                <strong>Positioning is not constraining price.</strong> Speculative length is modest and near historical norms, 
                leaving room for price to move without forced unwinds. Positioning neither confirms nor contradicts the valuation signal 
                — optionality remains intact.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ==================================================================
        # Z-SCORE CHART — Risk Visualization
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📈 Positioning Z-Score Over Time")
        
        if cftc_history is not None and len(cftc_history) > 0:
            # Calculate z-score if not in data
            if 'z_score' not in cftc_history.columns:
                mean_1y = cftc_history['net_position'].rolling(52).mean()
                std_1y = cftc_history['net_position'].rolling(52).std()
                cftc_history['z_score'] = (cftc_history['net_position'] - mean_1y) / std_1y
            
            fig = go.Figure()
            
            # Add regime bands (background)
            fig.add_hrect(y0=1.5, y1=3, fillcolor='rgba(239, 68, 68, 0.1)', line_width=0, 
                         annotation_text="Crowded Long", annotation_position="top right")
            fig.add_hrect(y0=-3, y1=-1.5, fillcolor='rgba(239, 68, 68, 0.1)', line_width=0,
                         annotation_text="Crowded Short", annotation_position="bottom right")
            
            # Add reference lines
            fig.add_hline(y=1.5, line_dash="dash", line_color="#EF4444", line_width=1, opacity=0.5)
            fig.add_hline(y=0, line_dash="solid", line_color="#666666", line_width=1)
            fig.add_hline(y=-1.5, line_dash="dash", line_color="#EF4444", line_width=1, opacity=0.5)
            
            # Primary: Z-Score
            fig.add_trace(go.Scatter(
                x=cftc_history['date'],
                y=cftc_history['z_score'],
                mode='lines',
                name='Z-Score (1Y)',
                line=dict(color='#9333EA', width=3),
                hovertemplate='<b>Z-Score:</b> %{y:.2f}σ<extra></extra>'
            ))
            
            # Secondary: Net Position (lighter, optional)
            fig.add_trace(go.Scatter(
                x=cftc_history['date'],
                y=cftc_history['net_position'] / 50000,  # Scale down for visibility
                mode='lines',
                name='Net Position (scaled)',
                line=dict(color='#888888', width=1, dash='dot'),
                opacity=0.3,
                yaxis='y2',
                hovertemplate='<b>Net:</b> %{y:.1f}k contracts<extra></extra>'
            ))
            
            fig.update_layout(
                height=400,
                plot_bgcolor='#1a1f2e',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'),
                showlegend=True,
                legend=dict(x=0.02, y=0.98, bgcolor='rgba(26, 31, 46, 0.8)'),
                margin=dict(l=40, r=40, t=20, b=40),
                yaxis=dict(
                    title=dict(text="Z-Score", font=dict(color='#888888')),
                    gridcolor='#2a2f3e',
                    range=[-2.5, 2.5]
                ),
                yaxis2=dict(
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    showticklabels=False
                ),
                xaxis=dict(
                    title=dict(text="", font=dict(color='#888888')),
                    gridcolor='#2a2f3e'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 **Historical positioning data available after CFTC data fetch**")
        
        # ==================================================================
        # POSITIONING TRIGGERS — When Does It Matter?
        # ==================================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(147, 51, 234, 0.1); border: 1px solid #9333EA; 
                    border-radius: 8px; padding: 1.5rem; margin: 1.5rem 0;">
            <div style="color: #9333EA; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 1rem;">⚡ Positioning Triggers</div>
            <div style="color: #d0d0d0; font-size: 0.95rem; line-height: 1.7;">
                <strong>Becomes a headwind if:</strong> Z-score > +1.5σ (crowded long)<br>
                <strong>Amplifies downside if:</strong> Valuation is rich + longs crowd in tandem<br>
                <strong>Matters most during:</strong> Macro or policy shocks that force unwinds<br><br>
                <em style="color: #888888;">Currently: Positioning is not amplifying or dampening the valuation signal. 
                Flows are not a constraint.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning("Positioning data not available. Run CFTC data fetch script.")

# =====================================================================
# Footer
# =====================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption("**Framework**: Layer 1 (Monthly Macro Valuation) + Layer 2 (Weekly Pressure Signals) + CFTC Positioning")
st.caption("**Last Updated**: Dashboard refreshes hourly • CFTC updates weekly (Tuesday)")

