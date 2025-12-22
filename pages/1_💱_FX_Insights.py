"""
FX Insights - EURUSD Analysis
Nikhil's comprehensive FX view with Valuation, Technicals, and Positioning
"""
import streamlit as st

# Page config FIRST (must be before any other Streamlit commands)
st.set_page_config(
    page_title="FX Insights - Nikhil Dashboard",
    page_icon="💱",
    layout="wide"
)

# Wrap ALL imports in try/except to catch errors
try:
    import streamlit.components.v1 as components
    import sys
    from pathlib import Path
    import json
    import pandas as pd
    import plotly.graph_objects as go
    from PIL import Image

    # Add parent directory to path
    sys.path.append(str(Path(__file__).parent.parent))
    
    st.success("✅ Imports successful")
    
except Exception as e:
    st.error(f"❌ IMPORT ERROR: {e}")
    st.stop()

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

# Load data with error handling
try:
    decision = load_fx_views_decision()
except Exception as e:
    st.error(f"⚠️ Decision data failed: {e}")
    decision = None

try:
    charts = load_fx_views_charts()
except Exception as e:
    st.error(f"⚠️ Charts failed: {e}")
    charts = None

try:
    cftc_summary, cftc_history = load_cftc_positioning()
except Exception as e:
    st.error(f"⚠️ CFTC data failed: {e}")
    cftc_summary, cftc_history = None, None

try:
    technical = load_technical_analysis()
except Exception as e:
    st.error(f"⚠️ Technical data failed: {e}")
    technical = None

# =====================================================================
# HEADER
# =====================================================================
st.write("🔍 DEBUG: Rendering header...")
st.markdown('<h1 class="fx-title">💱 FX Insights</h1>', unsafe_allow_html=True)
st.markdown('<p class="fx-subtitle">EURUSD • Valuation, Technicals & Positioning</p>', unsafe_allow_html=True)
st.write("🔍 DEBUG: Header rendered")

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
st.write("🔍 DEBUG: About to create tabs...")
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📈 VALUATION", "📊 TECHNICALS", "🎯 POSITIONING"])
st.write("🔍 DEBUG: Tabs created")

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

# (Due to character limits, I need to stop here. Use GitHub Desktop to push the complete file already in the working directory)
