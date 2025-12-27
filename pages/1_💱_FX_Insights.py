"""
FX Views - Complete Decision Page
Vertical flow with collapsible sections and chart explainers
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from pathlib import Path
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="FX Views - Nikhil Dashboard",
    page_icon="💱",
    layout="wide"
)

# Determine FX Views root
FX_VIEWS_ROOT = Path(__file__).parent.parent / 'FX Views'

# =====================================================================
# CSS - Modern Dark Theme
# =====================================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #1a1f2e 0%, #0f1419 100%);
        font-size: 18px;
    }
    
    .main { 
        background: transparent; 
        max-width: 1400px;
        padding: 20px 40px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(0, 255, 128, 0.3);
        font-size: 42px !important;
        margin-bottom: 30px !important;
    }
    
    h2 {
        color: #ffffff !important;
        font-size: 32px !important;
        margin-top: 40px !important;
        margin-bottom: 25px !important;
    }
    
    h3 {
        color: #ffffff !important;
        font-size: 26px !important;
        margin-top: 35px !important;
    }
    
    p, li, div {
        font-size: 18px;
        line-height: 1.7;
    }
    
    .section-note {
        font-style: italic;
        color: #999;
        font-size: 16px;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    
    /* Chart grid styling */
    .stImage {
        border-radius: 8px;
        border: 1px solid #2a2f3e;
    }
    
    /* Explainer boxes */
    .explainer-box {
        background-color: #1a1f2e;
        border: 1px solid #3a4254;
        border-radius: 8px;
        padding: 18px;
        margin: 15px 0;
    }
    
    .explainer-section {
        margin-bottom: 18px;
    }
    
    /* Expander spacing */
    .streamlit-expanderHeader {
        font-size: 24px !important;
        font-weight: 700 !important;
        padding: 20px 0 !important;
    }
    
    /* Add vertical spacing between major sections */
    [data-testid="stExpander"] {
        margin-top: 50px !important;
        margin-bottom: 50px !important;
    }
    
    /* Explainer content */
    [data-testid="stExpander"] p strong {
        font-size: 20px !important;
        color: #00ff88 !important;
    }
    
    /* Bullet points larger */
    [data-testid="stExpander"] li {
        margin-bottom: 8px;
        font-size: 17px;
    }
    
    .explainer-title {
        color: #00ff88;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .explainer-content {
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .right-now {
        background-color: #242b3d;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #ff6b35;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# Chart Explainer Configuration
# =====================================================================

CHART_EXPLAINERS = {
    'fair_value': {
        'purpose': 'Shows where EURUSD trades relative to the level implied by macro fundamentals (growth, rates, inflation, risk differentials).',
        'how_to_read': [
            'Green line = Spot EURUSD',
            'Orange dashed line = Macro fair value from ElasticNet model',
            'Gray bands = ±1σ and ±2σ boundaries',
            'Red dots = Periods where |z| ≥ 2σ (Break regime)'
        ]
    },
    'mispricing': {
        'purpose': 'Tracks how far EUR is from fair value in standard deviations over time.',
        'how_to_read': [
            'Z-score above +1σ = Rich (EUR expensive vs fundamentals)',
            'Z-score below -1σ = Cheap (EUR cheap vs fundamentals)',
            'Between ±1σ = Fair (aligned with fundamentals)',
            'Shaded regions show regime boundaries'
        ]
    },
    'pressure': {
        'purpose': 'Shows short-term flow and momentum signals indicating whether mispricing is expanding or compressing.',
        'how_to_read': [
            'Red bars = Expanding pressure (mispricing widening)',
            'Green bars = Compressing pressure (mean reversion)',
            'Bar intensity = Model confidence (high/medium/low)',
            'Last 52 weeks displayed for readability'
        ]
    },
    'decision_map': {
        'purpose': 'Combines valuation (x-axis) and pressure (y-axis) to visualize which regime we are in.',
        'how_to_read': [
            'X-axis = Valuation z-score (cheap left, rich right)',
            'Y-axis = Binary pressure (compress -1, expand +1)',
            'Four quadrants = Different decision regimes',
            'Red star = Current position'
        ]
    }
}

def get_right_now_text(chart_key, decision):
    """Generate dynamic 'Right now' text for each chart"""
    
    layers = decision.get('layers', {})
    val = layers.get('valuation', {})
    pressure = layers.get('pressure', {})
    
    if chart_key == 'fair_value':
        spot = val.get('spot', 0)
        fv = val.get('fair_value', 0)
        z = val.get('z_score', 0)
        date = val.get('date', 'N/A')
        return f"EURUSD is {z:+.2f}σ {'rich' if z > 0 else 'cheap'} versus macro fair value (FV={fv:.4f}, Spot={spot:.4f}). Macro inputs updated through {date}."
    
    elif chart_key == 'mispricing':
        z = val.get('z_score', 0)
        regime = val.get('status', 'N/A')
        return f"Current mispricing: {z:+.2f}σ ({regime}). Values above +1σ suggest EUR is expensive vs fundamentals; below -1σ suggests cheap."
    
    elif chart_key == 'pressure':
        label = pressure.get('label', 'neutral')
        prob = pressure.get('prob_expand', 0.5)
        conf = pressure.get('confidence', 'medium')
        date = pressure.get('date', 'N/A')
        direction = 'Expanding' if label == 'expand' else 'Compressing'
        return f"Mispricing pressure is {direction} with {int(prob*100 if label=='expand' else (1-prob)*100)}% confidence ({conf}), based on weekly rates, credit, volatility, liquidity, and FX momentum. Updated {date}."
    
    elif chart_key == 'decision_map':
        z = val.get('z_score', 0)
        label = pressure.get('label', 'neutral')
        quadrant = f"{'Rich' if z > 1 else 'Cheap' if z < -1 else 'Fair'} + {label.capitalize()}"
        return f"Current position: {quadrant} quadrant. This combination suggests: {decision.get('implication', 'mixed signals')}."
    
    return "Data not available."

# =====================================================================
# Load Data Functions
# =====================================================================

@st.cache_data(ttl=3600)
def load_decision_summary():
    """Load pre-computed decision summary"""
    path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fx_views_decision.json'
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return None

@st.cache_data(ttl=3600)
def load_technical_summary():
    """Load technical indicators summary"""
    path = FX_VIEWS_ROOT / 'technical_outputs' / 'eurusd_technical_summary.json'
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return None

@st.cache_data(ttl=3600)
def load_positioning_summary():
    """Load CFTC positioning summary"""
    path = FX_VIEWS_ROOT / 'cftc_outputs' / 'cftc_positioning_summary.json'
    csv_path = FX_VIEWS_ROOT / 'cftc_outputs' / 'cftc_eur_positioning.csv'
    
    try:
        with open(path, 'r') as f:
            summary = json.load(f)
        
        history = None
        if csv_path.exists():
            history = pd.read_csv(csv_path, parse_dates=['date'])
        
        return summary, history
    except:
        return None, None

# =====================================================================
# MAIN
# =====================================================================

st.markdown('<h1 style="font-size: 3rem; font-weight: 700;">📐 FX Views — EURUSD</h1>', unsafe_allow_html=True)
st.markdown("**Decision first, evidence second. Single vertical narrative flow.**")
st.markdown("---")

# Load all data
decision = load_decision_summary()

if decision is None:
    st.error("❌ FX Views data not found!")
    st.info("Run: `cd 'FX Views' && py generate_fx_views_complete.py`")
    st.stop()

tech_data = load_technical_summary()
pos_data, pos_history = load_positioning_summary()

# =====================================================================
# TOP: FX Decision Summary (NOT NUMBERED, ALWAYS VISIBLE)
# =====================================================================
st.markdown("### 💬 FX Decision Summary")

# Regime label
regime_label = decision.get('regime_label', 'N/A')
# Parse the nikhil_view into structured parts
nikhil_view = decision.get('nikhil_view', 'View not available.')
layers = decision.get('layers', {})

# Extract parts from nikhil_view (sentence 1 = state, sentence 2 = bias, sentence 3 = breaker)
sentences = nikhil_view.split('. ')
state_text = sentences[0] if len(sentences) > 0 else ''
bias_text = sentences[1] if len(sentences) > 1 else ''
breaker_text = '. '.join(sentences[2:]) if len(sentences) > 2 else ''

# Extract just the action from bias text (after "Bias: ")
if 'Bias:' in bias_text:
    action_text = bias_text.split('Bias:')[1].strip()
else:
    action_text = bias_text

# Regime headline (LARGEST text on page)
st.markdown(f"""
<div style='text-align: center; margin: 30px 0 20px 0;'>
    <div style='font-size: 48px; font-weight: 900; letter-spacing: 0.05em; color: #ff6b35; text-transform: uppercase; line-height: 1.1;'>
        {regime_label.replace(' + ', ' — ').replace('Pressure', '').replace('pressure', '').strip()}
    </div>
</div>
""", unsafe_allow_html=True)

# Actionable bias (large, on its own line)
st.markdown(f"""
<div style='text-align: center; margin: 25px 0 15px 0;'>
    <div style='font-size: 26px; font-weight: 700; color: #fff; line-height: 1.4;'>
        {action_text}
    </div>
</div>
""", unsafe_allow_html=True)

# What breaks it (smaller, italic)
st.markdown(f"""
<div style='text-align: center; margin: 10px 0 30px 0;'>
    <div style='font-size: 16px; font-style: italic; color: #999; line-height: 1.5;'>
        {breaker_text}
    </div>
</div>
""", unsafe_allow_html=True)

# State text (context line)
st.markdown(f"""
<div style='text-align: center; margin: 0 0 40px 0;'>
    <div style='font-size: 18px; color: #ccc; line-height: 1.6;'>
        {state_text}.
    </div>
</div>
""", unsafe_allow_html=True)

# Decision Matrix - Grouped Layout
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 28px; margin-bottom: 25px;'>Decision Matrix</h3>", unsafe_allow_html=True)

# Signal icons and data
val_signal = layers.get('valuation', {}).get('signal', 'N/A')
val_status = layers.get('valuation', {}).get('status', 'N/A')
val_icon = "🔴" if val_signal == "Rich" else "🟢" if val_signal == "Cheap" else "⚪"

pressure_signal = layers.get('pressure', {}).get('signal', 'N/A')
pressure_status = layers.get('pressure', {}).get('status', 'N/A')
pressure_icon = "🔴" if pressure_signal == "Expanding" else "🟢" if pressure_signal == "Compressing" else "⚪"

tech_signal = layers.get('technical', {}).get('signal', 'N/A')
tech_status = layers.get('technical', {}).get('status', 'N/A')
tech_icon = "🟢" if tech_signal == "Bullish" else "🔴" if tech_signal == "Bearish" else "⚪"

pos_signal = layers.get('positioning', {}).get('signal', 'N/A')
pos_status = layers.get('positioning', {}).get('status', 'N/A')
pos_icon = "🟠" if "Crowded" in pos_signal else "⚪"

# GROUP 1: Valuation + Pressure (Primary Signals)
st.markdown("<div style='margin-bottom: 10px; font-size: 16px; color: #888; text-transform: uppercase; letter-spacing: 0.1em;'>Primary Signals</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style='background-color: #1a1a1a; padding: 18px 24px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ff6b35;'>
    <span style='font-size: 18px; font-weight: 600; color: #ccc;'>{val_icon} Valuation:</span>
    <span style='font-size: 28px; font-weight: 800; color: #ff6b35; margin-left: 15px; text-transform: uppercase;'>{val_signal}</span>
    <span style='font-size: 14px; color: #777; margin-left: 15px;'>— {val_status}</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='background-color: #1a1a1a; padding: 18px 24px; border-radius: 10px; margin: 10px 0 25px 0; border-left: 5px solid #ff6b35;'>
    <span style='font-size: 18px; font-weight: 600; color: #ccc;'>{pressure_icon} Pressure:</span>
    <span style='font-size: 28px; font-weight: 800; color: #ff6b35; margin-left: 15px; text-transform: uppercase;'>{pressure_signal}</span>
    <span style='font-size: 14px; color: #777; margin-left: 15px;'>— {pressure_status}</span>
</div>
""", unsafe_allow_html=True)

# GROUP 2: Technicals + Positioning (Context Signals)
st.markdown("<div style='margin-bottom: 10px; font-size: 16px; color: #888; text-transform: uppercase; letter-spacing: 0.1em;'>Context Signals</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style='background-color: #1a1a1a; padding: 18px 24px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #00ff88;'>
    <span style='font-size: 18px; font-weight: 600; color: #ccc;'>{tech_icon} Technicals:</span>
    <span style='font-size: 28px; font-weight: 800; color: #00ff88; margin-left: 15px; text-transform: uppercase;'>{tech_signal}</span>
    <span style='font-size: 14px; color: #777; margin-left: 15px;'>— {tech_status}</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='background-color: #1a1a1a; padding: 18px 24px; border-radius: 10px; margin: 10px 0 30px 0; border-left: 5px solid #888;'>
    <span style='font-size: 18px; font-weight: 600; color: #ccc;'>{pos_icon} Positioning:</span>
    <span style='font-size: 28px; font-weight: 800; color: #ddd; margin-left: 15px; text-transform: uppercase;'>{pos_signal}</span>
    <span style='font-size: 14px; color: #777; margin-left: 15px;'>— {pos_status}</span>
</div>
""", unsafe_allow_html=True)

# Implication Bar (Taller, Higher Contrast, Verdict-like)
implication = decision.get('implication', 'N/A')
st.markdown(f"""
<div style='background: linear-gradient(135deg, #ff6b35 0%, #ff8c5a 100%); 
            padding: 25px 30px; border-radius: 12px; margin: 30px 0 40px 0; 
            border: 3px solid #ff6b35; box-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
            text-align: center;'>
    <div style='font-size: 16px; color: #fff; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin-bottom: 10px;'>
        ⚡ IMPLICATION
    </div>
    <div style='font-size: 22px; color: #fff; font-weight: 700; line-height: 1.4;'>
        {implication}
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# SECTION 1: VALUATION & PRESSURE (COLLAPSIBLE)
# =====================================================================
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

with st.expander("## 1️⃣ Valuation & Pressure", expanded=True):
    st.markdown('<div class="section-note">Layer 1 (Monthly Macro Fair Value) + Layer 2 (Weekly Pressure Binary)</div>', unsafe_allow_html=True)
    
    # 2x2 GRID FOR QUICK SCANNING
    # ROW 1
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("<h4 style='font-size: 20px; margin-bottom: 15px;'>1. Fair Value vs Spot</h4>", unsafe_allow_html=True)
        chart_path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fxviews_fair_value_monthly.png'
        if chart_path.exists():
            st.image(str(chart_path), use_container_width=True)
        
        with st.expander("📖 Explainer"):
            config = CHART_EXPLAINERS['fair_value']
            st.markdown(f"**Purpose:** {config['purpose']}")
            st.markdown("**How to Read:**")
            for item in config['how_to_read']:
                st.markdown(f"• {item}")
            st.markdown(f"**Right Now:** {get_right_now_text('fair_value', decision)}")
    
    with row1_col2:
        st.markdown("<h4 style='font-size: 20px; margin-bottom: 15px;'>2. Mispricing Z-Score</h4>", unsafe_allow_html=True)
        chart_path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fxviews_mispricing_z_monthly.png'
        if chart_path.exists():
            st.image(str(chart_path), use_container_width=True)
        
        with st.expander("📖 Explainer"):
            config = CHART_EXPLAINERS['mispricing']
            st.markdown(f"**Purpose:** {config['purpose']}")
            st.markdown("**How to Read:**")
            for item in config['how_to_read']:
                st.markdown(f"• {item}")
            st.markdown(f"**Right Now:** {get_right_now_text('mispricing', decision)}")
    
    # ROW 2
    st.markdown("")  # Small gap
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("<h4 style='font-size: 20px; margin-bottom: 15px;'>3. Pressure Timeline</h4>", unsafe_allow_html=True)
        chart_path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fxviews_pressure_weekly.png'
        if chart_path.exists():
            st.image(str(chart_path), use_container_width=True)
        
        with st.expander("📖 Explainer"):
            config = CHART_EXPLAINERS['pressure']
            st.markdown(f"**Purpose:** {config['purpose']}")
            st.markdown("**How to Read:**")
            for item in config['how_to_read']:
                st.markdown(f"• {item}")
            st.markdown(f"**Right Now:** {get_right_now_text('pressure', decision)}")
    
    with row2_col2:
        st.markdown("<h4 style='font-size: 20px; margin-bottom: 15px;'>4. Decision Map</h4>", unsafe_allow_html=True)
        chart_path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fxviews_decision_map.png'
        if chart_path.exists():
            st.image(str(chart_path), use_container_width=True)
        
        with st.expander("📖 Explainer"):
            config = CHART_EXPLAINERS['decision_map']
            st.markdown(f"**Purpose:** {config['purpose']}")
            st.markdown("**How to Read:**")
            for item in config['how_to_read']:
                st.markdown(f"• {item}")
            st.markdown(f"**Right Now:** {get_right_now_text('decision_map', decision)}")

# =====================================================================
# SECTION 2: TECHNICALS (COLLAPSIBLE)
# =====================================================================
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

with st.expander("## 2️⃣ Technicals", expanded=False):
    st.markdown('<div class="section-note">Technicals provide execution context, not valuation.</div>', unsafe_allow_html=True)
    
    if tech_data is None:
        st.warning("Technical data not available.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Regime", tech_data.get('regime', 'N/A'))
        with col2:
            st.metric("Technical Score", f"{tech_data.get('technical_score', 0):.1f}")
        with col3:
            rsi = tech_data.get('indicators', {}).get('RSI', 0)
            st.metric("RSI", f"{rsi:.1f}")
        with col4:
            spot = tech_data.get('spot', 0)
            st.metric("Spot", f"{spot:.4f}")
        
        # Narrative
        narrative = tech_data.get('narrative', 'No narrative available.')
        st.markdown(f"**Narrative:** {narrative}")
        
        # Key Levels
        st.markdown("### Key Reference Levels")
        key_levels = tech_data.get('key_levels', [])
        if key_levels:
            levels_df = pd.DataFrame(key_levels)
            st.dataframe(levels_df, use_container_width=True, hide_index=True)
        
        # Technical Chart
        chart_path = FX_VIEWS_ROOT / 'technical_outputs' / 'eurusd_technical_chart.html'
        if chart_path.exists():
            with open(chart_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            components.html(html_content, height=600, scrolling=True)

# =====================================================================
# SECTION 3: POSITIONING (COLLAPSIBLE)
# =====================================================================
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

with st.expander("## 3️⃣ Positioning", expanded=False):
    st.markdown('<div class="section-note">Positioning highlights asymmetry and tail risk.</div>', unsafe_allow_html=True)
    
    if pos_data is None:
        st.warning("Positioning data not available.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            state = pos_data.get('positioning_state', 'N/A')
            st.metric("State", state)
        with col2:
            percentile = pos_data.get('percentile', 0)
            st.metric("Percentile", f"{percentile:.0f}%")
        with col3:
            net = pos_data.get('net_position', 0)
            st.metric("Net Position", f"{net:,.0f}")
        with col4:
            z_1y = pos_data.get('z_1y', 0)
            st.metric("Z-Score (1Y)", f"{z_1y:.2f}")
        
        # Commentary
        commentary = pos_data.get('commentary', 'No commentary available.')
        st.markdown(f"**Commentary:** {commentary}")
        
        # Historical positioning chart
        if pos_history is not None and len(pos_history) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pos_history['date'],
                y=pos_history['net_position'],
                mode='lines',
                name='Net Position',
                line=dict(color='#00ff88', width=2)
            ))
            
            fig.update_layout(
                title='CFTC EUR Net Positioning (Weekly)',
                xaxis_title='Date',
                yaxis_title='Net Position (Contracts)',
                template='plotly_dark',
                height=400,
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='#e0e0e0')
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 40px;'>
    FX Views Framework | Layer 1: Monthly Macro Valuation (ElasticNet) | Layer 2: Weekly Binary Pressure (LightGBM)<br/>
    Technicals: Execution Context | Positioning: Asymmetry & Tail Risk<br/>
    <i>Framework suggests / balance of risks — NOT predictions</i>
</div>
""", unsafe_allow_html=True)
