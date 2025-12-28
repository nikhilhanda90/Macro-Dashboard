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
    
    /* === SIDEBAR NAVIGATION (SUPER PROMINENT) === */
    [data-testid="stSidebarNav"] {
        background-color: #0a0a0a;
        padding: 20px 15px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 2px solid #00ff80;
        box-shadow: 0 0 20px rgba(0, 255, 128, 0.3);
    }
    
    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    [data-testid="stSidebarNav"] li {
        margin: 12px 0 !important;
        list-style: none !important;
    }
    
    [data-testid="stSidebarNav"] a {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%) !important;
        border: 2px solid #00ff80 !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        color: #00ff80 !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        text-decoration: none !important;
        display: block !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 255, 128, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background: linear-gradient(135deg, #00ff80 0%, #00cc66 100%) !important;
        color: #000000 !important;
        border-color: #00ff80 !important;
        box-shadow: 0 0 25px rgba(0, 255, 128, 0.6) !important;
        transform: translateX(5px) !important;
    }
    
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg, #00ff80 0%, #00cc66 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        box-shadow: 0 0 30px rgba(0, 255, 128, 0.7) !important;
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

st.markdown("""
<div style='text-align: center; margin: 40px 0 50px 0;'>
    <div style='font-size: 80px; margin-bottom: 10px;'>🏦</div>
    <div style='font-size: 3.5rem; font-weight: 800; letter-spacing: 0.02em; color: #ffffff;'>
        FX Insights — EURUSD
    </div>
</div>
""", unsafe_allow_html=True)
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
# TOP: SYSTEM STATE + FX DECISION SUMMARY
# =====================================================================

layers = decision.get('layers', {})

# Get CFO view and analyst view
cfo_view = decision.get('cfo_view', 'View not available.')
analyst_view = decision.get('analyst_view', 'Detailed view not available.')

# Parse CFO view (ACTION|||... \n CONDITIONS|||...)
cfo_lines = cfo_view.split('\n')
action_text = ''
conditions_text = ''

for line in cfo_lines:
    if '|||' in line:
        label, content = line.split('|||', 1)
        if label.strip() == 'ACTION':
            action_text = content.strip()
        elif label.strip() == 'CONDITIONS':
            conditions_text = content.strip()

# TOP SECTION - "What do I do?" (2 lines)
st.markdown(f"""
<div style='margin: 30px 0 10px 0;'>
    <div style='font-size: 18px; font-weight: 700; color: #999; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 15px;'>
        ACTION
    </div>
    <div style='font-size: 26px; line-height: 1.5; color: #ff6b35; font-weight: 700; margin-bottom: 20px;'>
        {action_text}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='margin: 0 0 40px 0;'>
    <div style='font-size: 18px; font-weight: 700; color: #999; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px;'>
        CONDITIONS
    </div>
    <div style='font-size: 19px; line-height: 1.6; color: #e0e0e0; font-weight: 400;'>
        {conditions_text}
    </div>
</div>
""", unsafe_allow_html=True)

# ANALYST EXPLANATION (Collapsible)
with st.expander("📊 Analyst Explanation", expanded=False):
    st.markdown(f"""
    <div style='font-size: 17px; line-height: 1.9; color: #d0d0d0; font-weight: 400; white-space: pre-line;'>
        {analyst_view}
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# EVIDENCE SECTIONS (ALL COLLAPSED BY DEFAULT)
# =====================================================================
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

# Extract data for evidence checklist
val_signal_full = layers.get('valuation', {}).get('signal', 'N/A')
val_z_score = layers.get('valuation', {}).get('z_score', 0)
val_z = f"+{val_z_score:.2f}σ" if val_z_score > 0 else f"{val_z_score:.2f}σ"

pressure_signal_full = layers.get('pressure', {}).get('signal', 'N/A')
pressure_prob = layers.get('pressure', {}).get('prob_expand', 0.5)
pressure_conf = f"{int((1-pressure_prob)*100)}% conf" if pressure_signal_full == "Compressing" else f"{int(pressure_prob*100)}% conf"

tech_signal_full = layers.get('technical', {}).get('signal', 'N/A')
tech_status = layers.get('technical', {}).get('status', 'N/A')
tech_score = tech_status.split('(')[1].split(')')[0] if '(' in tech_status else "N/A"

pos_signal_full = layers.get('positioning', {}).get('signal', 'N/A')
pos_status = layers.get('positioning', {}).get('status', 'N/A')
pos_pct = pos_status.split('(')[1].split(')')[0] if '(' in pos_status else "N/A"

with st.expander("## 1️⃣ Valuation & Pressure", expanded=False):
    # Evidence Checklist at top
    st.markdown("**Evidence:**")
    st.markdown(f"""
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #ff6b35;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Valuation</span>
        <span style='font-size: 26px; font-weight: 800; color: #ff6b35; margin-left: 20px; text-transform: uppercase;'>{val_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{val_z}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #ff6b35;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Pressure</span>
        <span style='font-size: 26px; font-weight: 800; color: #ff6b35; margin-left: 20px; text-transform: uppercase;'>{pressure_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{pressure_conf}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
    
    # Hidden info panel - click to read
    with st.expander("ⓘ Valuation & Pressure Framework", expanded=False):
        st.markdown("""
        Valuation is produced by a macro fair-value model trained on relative growth, rates, inflation, credit, volatility, and liquidity conditions across the US and Euro Area. Multiple model classes were tested — including Ridge, Lasso, ElasticNet, and tree-based methods — across different feature sets and stability regimes.
        
        The final valuation model uses ElasticNet regression, selected deliberately for its ability to balance signal extraction and stability in a high-collinearity macro environment. ElasticNet delivered the most economically coherent coefficients and consistent out-of-sample behavior versus over-sparse linear models and over-fit tree-based alternatives.
        
        Pressure is modeled separately. A weekly LightGBM classifier estimates whether valuation gaps are more likely to expand or compress, using market-based inputs only. This layer does not forecast spot FX levels — it forecasts directional pressure on mispricing.
        
        The separation is intentional. Valuation defines where price is relative to macro fundamentals. Pressure defines how markets typically behave around that valuation. Timing and trade construction are completed using technicals and positioning.
        """)
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
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
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

with st.expander("## 2️⃣ Technicals", expanded=False):
    # Evidence Checklist
    st.markdown("**Evidence:**")
    st.markdown(f"""
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #00ff88;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Technicals</span>
        <span style='font-size: 26px; font-weight: 800; color: #00ff88; margin-left: 20px; text-transform: uppercase;'>{tech_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{tech_score}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)
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
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

with st.expander("## 3️⃣ Positioning", expanded=False):
    # Evidence Checklist
    st.markdown("**Evidence:**")
    st.markdown(f"""
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #888;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Positioning</span>
        <span style='font-size: 26px; font-weight: 800; color: #ddd; margin-left: 20px; text-transform: uppercase;'>{pos_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{pos_pct}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)
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

# =====================================================================
# DECISION MATRIX (TRACEABILITY TABLE - COLLAPSED BY DEFAULT)
# =====================================================================
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

with st.expander("## 🔍 Decision Matrix", expanded=False):
    st.markdown('<div class="section-note">Traceability table — shows how the final view was formed from all 4 layers.</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)
    
    # All 4 layers in one place for audit
    st.markdown(f"""
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #ff6b35;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Valuation</span>
        <span style='font-size: 26px; font-weight: 800; color: #ff6b35; margin-left: 20px; text-transform: uppercase;'>{val_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{val_z}</span>
    </div>
    
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #ff6b35;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Pressure</span>
        <span style='font-size: 26px; font-weight: 800; color: #ff6b35; margin-left: 20px; text-transform: uppercase;'>{pressure_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{pressure_conf}</span>
    </div>
    
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #00ff88;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Technicals</span>
        <span style='font-size: 26px; font-weight: 800; color: #00ff88; margin-left: 20px; text-transform: uppercase;'>{tech_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{tech_score}</span>
    </div>
    
    <div style='background-color: #1a1a1a; padding: 16px 24px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #888;'>
        <span style='font-size: 16px; font-weight: 500; color: #999;'>Positioning</span>
        <span style='font-size: 26px; font-weight: 800; color: #ddd; margin-left: 20px; text-transform: uppercase;'>{pos_signal_full}</span>
        <span style='font-size: 18px; color: #ccc; margin-left: 20px;'>{pos_pct}</span>
    </div>
    """, unsafe_allow_html=True)
