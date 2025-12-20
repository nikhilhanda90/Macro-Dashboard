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
        # Decision summary - Top Right
        inputs = decision['inputs']
        stance = decision['stance']
        
        # Create top section with metrics on the right
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.info(f"**{stance['stance_title']}**: {stance['stance_summary']}")
        
        with col_right:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%); 
                        border: 2px solid #00A676; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="margin-bottom: 1rem;">
                    <div style="color: #888888; font-size: 0.8rem; text-transform: uppercase;">Valuation</div>
                    <div style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; font-family: 'Courier New', monospace;">{inputs['z_val']:+.2f}σ</div>
                    <div style="color: #00A676; font-size: 0.85rem;">{inputs['val_bucket'].replace('_', ' ')}</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="color: #888888; font-size: 0.8rem; text-transform: uppercase;">Pressure</div>
                    <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700;">{inputs['pressure_dir'].upper()}</div>
                    <div style="color: #00A676; font-size: 0.85rem;">{inputs['pressure_conf'].upper()} confidence</div>
                </div>
                <div>
                    <div style="color: #888888; font-size: 0.8rem; text-transform: uppercase;">Stance</div>
                    <div style="background: #00A676; color: #FFFFFF; padding: 0.5rem 1rem; border-radius: 8px; 
                                font-weight: 700; font-size: 1.2rem; margin-top: 0.5rem;">{stance['stance_badge']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chart 1: Fair Value & Regime Bands
        st.markdown("#### Chart 1: Fair Value & Regime Bands (Monthly)")
        st.image(str(charts['fair_value']), use_column_width=True)
        
        # Chart 2: Mispricing Z-Score
        st.markdown("#### Chart 2: Mispricing Z-Score Time Series")
        st.image(str(charts['mispricing']), use_column_width=True)
        
        # Chart 3: Weekly Pressure
        st.markdown("#### Chart 3: Weekly Pressure Panel")
        st.image(str(charts['pressure']), use_column_width=True)
        
        # Chart 4: Decision Map
        st.markdown("#### Chart 4: Decision Map (Valuation × Pressure)")
        st.image(str(charts['decision_map']), use_column_width=True)
        
        # Nikhil's View
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="nikhil-view">
            <div class="view-header">💬 Nikhil's View on Valuation</div>
            <div class="view-text">
                EUR looks rich vs macro fundamentals. Layer 1 fair value model (ElasticNet) shows +1.3σ mispricing, 
                while Layer 2 weekly pressure suggests compression underway. Decision table says "Overvaluation Fading" 
                — a setup that historically favors mean reversion. Not a high-conviction fade yet, but the asymmetry 
                leans downside if macro or policy dynamics disappoint.
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
        # Top section: Score + Narrative
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown(f"""
            <div style="background: rgba(26, 31, 46, 0.7); border-left: 4px solid #00A676; 
                        border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
                <div style="font-size: 1.05rem; color: #e0e0e0; line-height: 1.7;">
                    {technical['narrative']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            # Technical Score Card
            score = technical['technical_score']
            regime = technical['regime']
            
            score_color = '#00A676' if score > 0 else '#EF4444' if score < 0 else '#888888'
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #242b3d 0%, #1a1f2e 100%); 
                        border: 2px solid {score_color}; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="color: #888888; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 0.5rem;">
                    Technical Score
                </div>
                <div style="color: {score_color}; font-size: 2.5rem; font-weight: 700; font-family: 'Courier New', monospace; margin-bottom: 0.5rem;">
                    {score:+.1f}
                </div>
                <div style="background: {score_color}; color: #FFFFFF; padding: 0.5rem 1rem; border-radius: 8px; 
                            font-weight: 700; font-size: 1.1rem; margin-top: 0.75rem;">
                    {regime}
                </div>
                <div style="color: #888888; font-size: 0.75rem; margin-top: 0.75rem;">
                    Range: -3 to +3
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Candlestick Chart (if available)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📈 Price Chart")
        
        chart_path = Path(__file__).parent.parent / 'FX Views' / 'technical_outputs' / 'eurusd_technical_chart.html'
        if chart_path.exists():
            with open(chart_path, 'r', encoding='utf-8') as f:
                chart_html = f.read()
            components.html(chart_html, height=1200, scrolling=True)
        else:
            st.info("📊 **Candlestick chart available after running chart generator**")
        
        # Key Levels
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📍 Key Levels")
        
        levels = technical.get('key_levels', [])
        if levels:
            for level in levels:
                level_type_color = '#00A676' if level['type'] == 'Support' else '#EF4444'
                dist_sign = '+' if level['distance_pct'] > 0 else ''
                
                st.markdown(f"""
                <div style="background: rgba(26, 31, 46, 0.5); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;
                            display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #FFFFFF; font-weight: 600; font-size: 1.05rem;">{level['name']}</span>
                        <span style="color: {level_type_color}; font-size: 0.85rem; margin-left: 0.75rem;">• {level['type']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #FFFFFF; font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: 600;">
                            {level['price']:.4f}
                        </div>
                        <div style="color: #888888; font-size: 0.85rem;">
                            {dist_sign}{level['distance_pct']:.2f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Key Indicators
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Key Indicators")
        
        indicators = technical.get('indicators', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("RSI (14)", f"{indicators.get('RSI', 0):.1f}")
            st.caption("30-70 range")
        
        with col2:
            macd_val = indicators.get('MACD', 0)
            st.metric("MACD", f"{macd_val:.4f}")
            st.caption("vs Signal")
        
        with col3:
            st.metric("50-day MA", f"{indicators.get('SMA_50', 0):.4f}")
            st.caption(f"Spot: {technical['spot']:.4f}")
        
        with col4:
            st.metric("200-day MA", f"{indicators.get('SMA_200', 0):.4f}")
            st.caption("Trend anchor")
        
        # Nikhil's View
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="nikhil-view">
            <div class="view-header">💬 Nikhil's View on Technicals</div>
            <div class="view-text">
                Technicals are {regime.lower()} with a score of {score:+.1f}/3. Price remains below key resistance at the 200-day MA, 
                with momentum showing no strong conviction either way. The compressed volatility (BB width at 
                {technical['percentiles'].get('bb_width_pct', 0):.0f}%ile) suggests the market is coiling for a directional break. 
                Until price reclaims the 50-day MA decisively, the technical bias leans cautious.
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
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Net Position", f"{cftc_summary['net_position']:+,}", "contracts")
        with col2:
            st.metric("Z-Score (1Y)", f"{cftc_summary['z_1y']:+.2f}σ")
        with col3:
            st.metric("State", cftc_summary['positioning_state'])
        
        st.info(f"**Risk Asymmetry**: {cftc_summary['commentary']}")
        
        # Historical chart if available
        if cftc_history is not None and len(cftc_history) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=cftc_history['date'],
                y=cftc_history['net_position'],
                mode='lines',
                name='Net Position',
                line=dict(color='#00A676', width=2)
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="#666666")
            fig.update_layout(
                height=300,
                plot_bgcolor='#1a1f2e',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=40)
            )
            st.plotly_chart(fig, use_column_width=True)
        
        # Nikhil's View
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="nikhil-view">
            <div class="view-header">💬 Nikhil's View on Positioning</div>
            <div class="view-text">
                Positioning is {cftc_summary['positioning_state'].lower()} ({cftc_summary['z_1y']:+.2f}σ vs 1Y mean), 
                suggesting limited crowding-related asymmetry. Speculative positioning neither supports nor opposes 
                the valuation view. If positioning shifts materially long while EUR stays rich, fragility increases. 
                For now, it's a neutral input.
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

