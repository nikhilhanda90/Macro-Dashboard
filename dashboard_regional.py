"""
Nikhil Dashboard
Macro & FX Analysis Platform
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import config_cycle_v2 as config
from data_fetcher import DataFetcher
from analyzer_cycle_v2 import CycleAnalyzerV2
from commentary_engine import CommentaryEngine

# Try to import Eurostat and Country analyzer
try:
    from data_eurostat import EurostatFetcher
    from analyzer_country import CountryAnalyzer
    COUNTRY_ANALYSIS_AVAILABLE = True
except ImportError:
    COUNTRY_ANALYSIS_AVAILABLE = False

st.set_page_config(
    page_title="Macro View",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def format_indicator_value(series_id, raw_value):
    """
    Format indicator values for display based on their type.
    - EA_UNEMPLOYMENT: already percent (6.5 -> 6.5%)
    - Japan Exports/Imports: billions of yen -> trillions
    """
    if raw_value is None or pd.isna(raw_value):
        return "N/A", ""
    
    # Euro Area Unemployment Rate (already a percentage)
    if series_id in ["EA_UNEMPLOYMENT", "LRUNTTTTEZM156S", "LRHUTTTTEA156S", "EA_UNEMP"]:
        return f"{raw_value:.1f}", "%"
    
    # Japan Exports/Imports (billions of yen → trillions)
    if series_id in ["XTEXVA01JPM664S", "XTIMVA01JPM664S"]:
        value_trillions = raw_value / 1000.0  # assuming input is in billions
        return f"{value_trillions:,.1f}", "Trillion yen"
    
    # Default: return value as-is
    return raw_value, ""

# Custom CSS - Modern Dark Theme
st.markdown("""
<style>
    /* === MODERN DARK THEME - Main Background === */
    .main {
        padding: 2rem;
        background: linear-gradient(to bottom, #1a1f2e 0%, #0f1419 100%);
    }
    
    .stApp {
        background: linear-gradient(to bottom, #1a1f2e 0%, #0f1419 100%);
    }
    
    /* === Text Colors === */
    .stMarkdown, .stMarkdown p {
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(0, 255, 128, 0.3);
        font-weight: 700;
    }
    
    .stCaption {
        color: #888888 !important;
    }
    
    /* === Section Titles === */
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00ff80;
        color: #ffffff !important;
    }
    
    /* === Containers & Cards === */
    .element-container {
        background-color: transparent;
    }
    
    [data-testid="stHorizontalBlock"] {
        background-color: #0a0a0a;
    }
    
    /* === Metrics === */
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0, 255, 128, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #00ff80 !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
    }
    
    /* === Buttons === */
    .stButton button {
        background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
        color: #00ff80;
        border: 2px solid #00ff80;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s;
        text-shadow: 0 0 10px rgba(0, 255, 128, 0.5);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #00ff80 0%, #00cc66 100%);
        color: #000000;
        box-shadow: 0 0 25px rgba(0, 255, 128, 0.6);
        transform: translateY(-2px);
    }
    
    /* === Columns === */
    div[data-testid="column"] {
        background-color: #0f0f0f;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* === Expanders === */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    /* === Dataframes === */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    
    .dataframe th {
        background-color: #00ff80 !important;
        color: #000000 !important;
        font-weight: 700;
    }
    
    .dataframe td {
        color: #ffffff !important;
        border-color: #333 !important;
    }
    
    /* === Charts === */
    .js-plotly-plot {
        background-color: transparent !important;
    }
    
    /* === Sidebar === */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 2px solid #00ff80;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* === Input Elements === */
    .stTextInput input, .stSelectbox select {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    
    /* === Glow Effects === */
    .stMarkdown > div {
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
    }
    
    /* === Links === */
    a {
        color: #00ff80 !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #00cc66 !important;
        text-shadow: 0 0 10px rgba(0, 255, 128, 0.5);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_data():
    """Load both US and Eurozone data, filtering out stale indicators"""
    fetcher = DataFetcher()
    analyzer = CycleAnalyzerV2()
    
    # Fetch all indicators (US + Eurozone)
    all_results = {}
    stale_indicators = []
    
    total_indicators = len(config.INDICATORS)
    
    for idx, (series_id, indicator_config) in enumerate(config.INDICATORS.items(), 1):
        try:
            print(f"[{idx}/{total_indicators}] Loading {indicator_config.get('name', series_id)}...")
            data_info = fetcher.get_indicator(series_id, indicator_config)
            
            # Skip if data is None (stale or unavailable)
            if data_info is None or data_info.get('data') is None:
                # Try to fetch data anyway to get last date
                try:
                    raw_df = fetcher.get_fred_series(series_id)
                    if raw_df is not None and not raw_df.empty:
                        last_date = raw_df['date'].max().strftime('%Y-%m-%d')
                        stale_indicators.append((indicator_config.get('name', series_id), last_date))
                    else:
                        stale_indicators.append((indicator_config.get('name', series_id), 'No data'))
                except:
                    stale_indicators.append((indicator_config.get('name', series_id), 'Unknown'))
                continue
            
            # Analyze with new analyzer
            try:
                analysis = analyzer.analyze_indicator(
                    data_info['data'],
                    series_id=series_id,
                    name=data_info['name'],
                    region=indicator_config.get('region', 'US'),
                    old_config=indicator_config
                )
            except Exception as e:
                stale_indicators.append((indicator_config.get('name', series_id), f'Analysis error: {str(e)[:50]}'))
                continue
            
            if analysis:
                all_results[series_id] = {
                    **data_info,
                    **analysis,
                    'region': indicator_config.get('region', 'US'),
                    'indicator_type': indicator_config.get('indicator_type')
                }
        except Exception as e:
            stale_indicators.append((indicator_config.get('name', series_id), f'Error: {str(e)[:30]}'))
            continue
    
    return all_results, stale_indicators

def get_percentile_color(pct):
    """Get color based on percentile"""
    if pct is None:
        return '#cccccc'  # Gray for missing data
    if pct >= 80:
        return '#ffd700'  # Gold
    elif pct >= 60:
        return '#90ee90'  # Light green
    elif pct >= 40:
        return '#add8e6'  # Light blue
    elif pct >= 20:
        return '#d8bfd8'  # Lavender
    else:
        return '#ffb6c1'  # Light pink

def get_qualitative_label(pct, inverted=False):
    """Get qualitative label based on percentile"""
    if pct is None:
        return "⚫ No Data"
    
    if inverted:
        if pct >= 80:
            return "🔴 Tight / Stressed"
        elif pct >= 60:
            return "🟡 Elevated"
        elif pct <= 20:
            return "🟢 Loose / Calm"
        elif pct <= 40:
            return "🔵 Below Average"
        else:
            return "⚪ Neutral"
    else:
        if pct >= 80:
            return "🟢 Very High"
        elif pct >= 60:
            return "🔵 Above Average"
        elif pct <= 20:
            return "🔴 Very Low"
        elif pct <= 40:
            return "🟡 Below Average"
        else:
            return "⚪ Neutral"

def calculate_summary_health(analysis_results, region, indicator_type):
    """Calculate health score for a region's indicator type"""
    filtered = [v for v in analysis_results.values() 
                if v.get('region') == region 
                and v.get('indicator_type') == indicator_type
                and not v.get('hidden', False)  # Exclude hidden indicators
                and not v.get('contextual', False)]  # Exclude contextual indicators from scoring
    
    if not filtered:
        return "Neutral", 50
    
    # Average percentile (excluding None values)
    percentiles = [v.get('percentile_all') for v in filtered if v.get('percentile_all') is not None]
    
    if not percentiles:
        return "Neutral", 50
    
    avg_pct = sum(percentiles) / len(percentiles)
    
    if avg_pct >= 65:
        return "Strong", avg_pct
    elif avg_pct <= 35:
        return "Weak", avg_pct
    else:
        return "Neutral", avg_pct

def create_summary_boxes(analysis_results, region):
    """Create three summary boxes for Leading/Coincident/Lagging"""
    cols = st.columns(3)
    
    types = ['Leading', 'Coincident', 'Lagging']
    emojis = ['📈', '📊', '📉']
    
    for idx, (ind_type, emoji) in enumerate(zip(types, emojis)):
        with cols[idx]:
            health, score = calculate_summary_health(analysis_results, region, ind_type)
            
            color = '#7cb342' if health == 'Strong' else '#d32f2f' if health == 'Weak' else '#FFA500'
            
            st.markdown(f"""
            <div style='background-color: {color}; padding: 1.5rem; border-radius: 10px; text-align: center;'>
                <div style='font-size: 1rem; color: white; margin-bottom: 0.5rem;'>{emoji} {ind_type}</div>
                <div style='font-size: 2rem; font-weight: bold; color: white;'>{health}</div>
                <div style='font-size: 0.9rem; color: white;'>Avg: {score:.0f}th percentile</div>
            </div>
            """, unsafe_allow_html=True)

def create_indicator_cards(analysis_results, indicator_type, region):
    """Create card grid for indicators"""
    filtered = [
        (k, v) for k, v in analysis_results.items()
        if v.get('indicator_type') == indicator_type 
        and v.get('region') == region
        and not v.get('hidden', False)  # Exclude hidden indicators
    ]
    
    if not filtered:
        st.info(f"No {indicator_type} indicators for {region}")
        return
    
    # Sort by name
    filtered.sort(key=lambda x: x[1].get('name', ''))
    
    # Create 4-column grid
    cols_per_row = 4
    for i in range(0, len(filtered), cols_per_row):
        row_items = filtered[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        
        for idx, (series_id, result) in enumerate(row_items):
            with cols[idx]:
                with st.container():
                    # Header
                    st.markdown(f"<div style='color: #00ff80; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;'>{result.get('name', 'Unknown')}</div>", unsafe_allow_html=True)
                    
                    # Fun line (catchy one-liner)
                    fun_line = result.get('fun_line', '')
                    if fun_line:
                        st.markdown(f"<div style='color: #aaa; font-size: 0.85rem; font-style: italic; margin-bottom: 0.5rem;'>{fun_line}</div>", unsafe_allow_html=True)
                    
                    # Main value - use custom formatter for special cases
                    raw_value = result.get('current_value')
                    formatted_value, custom_unit = format_indicator_value(series_id, raw_value)
                    
                    if custom_unit:
                        # Custom formatting was applied (e.g., EA_UNEMPLOYMENT)
                        value_str = f"{formatted_value} {custom_unit}"
                    else:
                        # Standard formatting
                        is_inflation = result.get('is_inflation', False)
                        if is_inflation:
                            value_str = f"{formatted_value}% YoY"
                        else:
                            unit = result.get('unit', '')
                            value_str = f"{formatted_value} {unit}" if unit else str(formatted_value)
                    
                    st.markdown(f"<div style='color: #fff; font-weight: 700; font-size: 1.8rem; margin: 0.5rem 0;'>{value_str}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: #888; font-size: 0.8rem; margin-bottom: 0.8rem;'>{result.get('current_date', 'N/A')}</div>", unsafe_allow_html=True)
                    
                    # Percentile boxes
                    col1, col2 = st.columns(2)
                    
                    percentile_all = result.get('percentile_all')
                    percentile_recent = result.get('percentile_recent')
                    inverted = result.get('inverted', False)
                    
                    with col1:
                        color = get_percentile_color(percentile_all)
                        pct_display = f"{percentile_all}%" if percentile_all is not None else "N/A"
                        st.markdown(f"""
                        <div style='background-color: {color}; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid #000;'>
                            <div style='font-size: 0.75rem; color: #000; font-weight: 700; opacity: 1;'>ALL-TIME</div>
                            <div style='font-size: 1.1rem; font-weight: bold; color: #000; opacity: 1; margin-top: 4px;'>{pct_display}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        color = get_percentile_color(percentile_recent)
                        pct_display = f"{percentile_recent}%" if percentile_recent is not None else "N/A"
                        st.markdown(f"""
                        <div style='background-color: {color}; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid #000;'>
                            <div style='font-size: 0.75rem; color: #000; font-weight: 700; opacity: 1;'>5-YEAR</div>
                            <div style='font-size: 1.1rem; font-weight: bold; color: #000; opacity: 1; margin-top: 4px;'>{pct_display}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Qualitative label
                    label = get_qualitative_label(percentile_all, inverted)
                    st.markdown(f"<div style='color: #00ff80; font-weight: 700; font-size: 1rem; margin: 0.8rem 0 0.5rem 0; text-shadow: 0 0 10px rgba(0,255,128,0.3);'>{label}</div>", unsafe_allow_html=True)
                    
                    # Dynamic interpretation (what it means now)
                    dynamic_line = result.get('dynamic_line', '')
                    if dynamic_line:
                        st.markdown(f"<div style='color: #00cc99; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600;'>{dynamic_line}</div>", unsafe_allow_html=True)
                    
                    # Trend label + explainer
                    trend_label = result.get('trend_label', 'Flat →')
                    trend_explainer = result.get('trend_explainer', '')
                    st.markdown(f"<div style='color: #00ff80; font-weight: 600; font-size: 0.95rem; margin: 0.5rem 0 0.2rem 0;'>{trend_label}</div>", unsafe_allow_html=True)
                    if trend_explainer:
                        st.markdown(f"<div style='color: #888; font-size: 0.75rem; margin-bottom: 0.5rem;'>{trend_explainer}</div>", unsafe_allow_html=True)
                    
                    # Mini chart
                    df = result.get('data')
                    if df is not None and not df.empty:
                        df_recent = df.sort_values('date').tail(100)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_recent['date'],
                            y=df_recent['value'],
                            mode='lines',
                            line=dict(color='#0068c9', width=1.5),
                            showlegend=False
                        ))
                        fig.update_layout(
                            height=60,
                            margin=dict(l=0, r=0, t=0, b=0),
                            xaxis=dict(showticklabels=False, showgrid=False),
                            yaxis=dict(showticklabels=False, showgrid=False),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{series_id}_{indicator_type}")
                    
                    st.markdown("---")

def create_macro_state_summary(analysis_results, region):
    """
    Layer 2: Macro State Summary - Show Leading/Coincident/Lagging status badges
    """
    # Categorize indicators
    categories = {'Leading': [], 'Coincident': [], 'Lagging': []}
    
    for series_id, result in analysis_results.items():
        if result.get('region') == region and not result.get('hidden', False):
            ind_type = result.get('indicator_type')
            if ind_type in categories:
                categories[ind_type].append(result)
    
    # Calculate aggregate status for each category
    def get_category_status(indicators):
        if not indicators:
            return "⚪", "No Data", "#888888"
        
        # Count percentiles
        high_count = sum(1 for ind in indicators if (ind.get('percentile_all') or 0) > 70)
        low_count = sum(1 for ind in indicators if (ind.get('percentile_all') or 0) < 30)
        total = len([ind for ind in indicators if ind.get('percentile_all') is not None])
        
        if total == 0:
            return "⚪", "Flat", "#888888"
        
        high_ratio = high_count / total
        low_ratio = low_count / total
        
        if high_ratio > 0.5:
            return "🟢", "Strong", "#00ff80"
        elif low_ratio > 0.5:
            return "🔴", "Weak", "#ff4444"
        elif high_ratio > 0.3:
            return "🟡", "Mixed-High", "#ffaa00"
        elif low_ratio > 0.3:
            return "🟠", "Softening", "#ff8800"
        else:
            return "⚪", "Neutral", "#888888"
    
    # Get status for each
    leading_emoji, leading_status, leading_color = get_category_status(categories['Leading'])
    coincident_emoji, coincident_status, coincident_color = get_category_status(categories['Coincident'])
    lagging_emoji, lagging_status, lagging_color = get_category_status(categories['Lagging'])
    
    # Render state summary
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                border: 1px solid #3a4254;
                margin: 2rem 0;'>
        <div style='color: #ffffff; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.5rem; text-align: center;'>
            MACRO STATE — {region.upper()}
        </div>
        <div style='display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 2rem;'>
            <div style='text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>{leading_emoji}</div>
                <div style='color: {leading_color}; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem;'>{leading_status}</div>
                <div style='color: #888888; font-size: 0.85rem;'>Leading</div>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>{coincident_emoji}</div>
                <div style='color: {coincident_color}; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem;'>{coincident_status}</div>
                <div style='color: #888888; font-size: 0.85rem;'>Coincident</div>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>{lagging_emoji}</div>
                <div style='color: {lagging_color}; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem;'>{lagging_status}</div>
                <div style='color: #888888; font-size: 0.85rem;'>Lagging</div>
            </div>
        </div>
        <div style='text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #3a4254;'>
            <div style='color: #d0d0d0; font-size: 0.95rem; line-height: 1.6;'>
                Early-cycle signals are {leading_status.lower()}, current activity is {coincident_status.lower()}, and lagging data shows {lagging_status.lower()} conditions.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_macro_relative_view(analysis_results):
    """
    US vs Eurozone macro comparison - executive summary for FX context
    """
    # Extract macro states for both regions
    def get_region_state(region):
        filtered = [v for v in analysis_results.values() if v.get('region') == region]
        
        if not filtered:
            return None
        
        # Growth state (from Leading indicators)
        leading = [v for v in filtered if v.get('indicator_type') == 'Leading']
        leading_pcts = [v.get('percentile_all') for v in leading if v.get('percentile_all') is not None]
        
        if leading_pcts:
            avg_leading = sum(leading_pcts) / len(leading_pcts)
            if avg_leading > 65:
                growth_state = "strong"
            elif avg_leading < 35:
                growth_state = "weak"
            else:
                growth_state = "moderate"
        else:
            growth_state = "unclear"
        
        # Inflation state (from CPI indicators)
        inflation_indicators = [v for v in filtered if 'inflation' in v.get('name', '').lower() or 'cpi' in v.get('name', '').lower()]
        if inflation_indicators:
            inflation_pct = inflation_indicators[0].get('percentile_all')
            if inflation_pct and inflation_pct > 70:
                inflation_state = "elevated"
            elif inflation_pct and inflation_pct < 30:
                inflation_state = "subdued"
            else:
                inflation_state = "moderate"
        else:
            inflation_state = "unclear"
        
        # Policy bias (from yield/rate indicators)
        policy_indicators = [v for v in filtered if 'yield' in v.get('name', '').lower() or 'rate' in v.get('name', '').lower()]
        if policy_indicators:
            policy_pct = policy_indicators[0].get('percentile_all')
            if policy_pct and policy_pct > 60:
                policy_bias = "restrictive"
            elif policy_pct and policy_pct < 40:
                policy_bias = "accommodative"
            else:
                policy_bias = "neutral"
        else:
            policy_bias = "neutral"
        
        # Recession risk (from coincident weakness)
        coincident = [v for v in filtered if v.get('indicator_type') == 'Coincident']
        coincident_pcts = [v.get('percentile_all') for v in coincident if v.get('percentile_all') is not None]
        
        if coincident_pcts:
            avg_coincident = sum(coincident_pcts) / len(coincident_pcts)
            if avg_coincident < 30 and avg_leading < 35:
                recession_risk = "elevated"
            elif avg_coincident < 40:
                recession_risk = "moderate"
            else:
                recession_risk = "low"
        else:
            recession_risk = "unclear"
        
        return {
            'growth_state': growth_state,
            'inflation_state': inflation_state,
            'policy_bias': policy_bias,
            'recession_risk': recession_risk
        }
    
    us_state = get_region_state('US')
    eu_state = get_region_state('Eurozone')
    
    if not us_state or not eu_state:
        return  # Skip if data unavailable
    
    # Compare and determine advantage
    us_score = 0
    eu_score = 0
    
    # Growth comparison (stronger = advantage)
    if us_state['growth_state'] == 'strong' and eu_state['growth_state'] != 'strong':
        us_score += 1
    elif eu_state['growth_state'] == 'strong' and us_state['growth_state'] != 'strong':
        eu_score += 1
    
    # Inflation comparison (lower = advantage)
    if us_state['inflation_state'] == 'subdued' and eu_state['inflation_state'] == 'elevated':
        us_score += 1
    elif eu_state['inflation_state'] == 'subdued' and us_state['inflation_state'] == 'elevated':
        eu_score += 1
    
    # Policy comparison (more accommodative when growth weak = advantage)
    if us_state['policy_bias'] == 'accommodative' and eu_state['policy_bias'] == 'restrictive':
        us_score += 1
    elif eu_state['policy_bias'] == 'accommodative' and us_state['policy_bias'] == 'restrictive':
        eu_score += 1
    
    # Recession risk (lower = advantage)
    if us_state['recession_risk'] == 'low' and eu_state['recession_risk'] in ['moderate', 'elevated']:
        us_score += 1
    elif eu_state['recession_risk'] == 'low' and us_state['recession_risk'] in ['moderate', 'elevated']:
        eu_score += 1
    
    # Determine headline
    if us_score >= 2:
        headline = "US macro shows relative advantage over Eurozone"
        fx_bias = "USD"
        fx_color = "#00A676"
    elif eu_score >= 2:
        headline = "Eurozone macro shows relative advantage over US"
        fx_bias = "EUR"
        fx_color = "#00A676"
    else:
        headline = "US-Eurozone macro divergence limited"
        fx_bias = "mixed"
        fx_color = "#888888"
    
    # Generate paragraph
    if fx_bias == "USD":
        paragraph = f"US macro conditions remain more supportive than Eurozone. Growth momentum is {us_state['growth_state']} in the US versus {eu_state['growth_state']} in Europe, while policy settings and recession risks tilt favorably toward US assets. This macro divergence continues to favor USD over EUR unless Eurozone growth improves materially."
    elif fx_bias == "EUR":
        paragraph = f"Eurozone macro conditions are improving relative to the US. Growth momentum is {eu_state['growth_state']} in Europe versus {us_state['growth_state']} in the US, creating a more balanced outlook. This narrowing divergence reduces the structural headwind for EUR, though a sustained shift would require confirmation across multiple indicators."
    else:
        paragraph = f"US and Eurozone macro conditions are converging. Both regions show {us_state['growth_state']} growth momentum, with similar policy stances and recession risks. The absence of a clear macro advantage limits directional conviction on USD/EUR—FX moves are more likely driven by near-term catalysts than structural divergence."
    
    # Comparison table
    comparison_data = {
        'Dimension': ['Growth Momentum', 'Inflation Pressure', 'Policy Stance', 'Recession Risk'],
        'United States': [
            us_state['growth_state'].capitalize(),
            us_state['inflation_state'].capitalize(),
            us_state['policy_bias'].capitalize(),
            us_state['recession_risk'].capitalize()
        ],
        'Eurozone': [
            eu_state['growth_state'].capitalize(),
            eu_state['inflation_state'].capitalize(),
            eu_state['policy_bias'].capitalize(),
            eu_state['recession_risk'].capitalize()
        ]
    }
    
    df_compare = pd.DataFrame(comparison_data)
    
    # FX implication
    if fx_bias == "USD":
        fx_implication = "Macro divergence supports USD strength unless Eurozone data surprises positively."
    elif fx_bias == "EUR":
        fx_implication = "Narrowing macro divergence reduces EUR headwinds and opens room for EUR recovery."
    else:
        fx_implication = "Balanced macro backdrop limits structural FX bias—watch for tactical catalysts."
    
    # Render
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                border: 2px solid {fx_color};
                margin: 2rem 0;'>
        <div style='color: {fx_color}; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;'>
            🌍 Macro Relative View: US vs Eurozone
        </div>
        <div style='color: #ffffff; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;'>
            {headline}
        </div>
        <div style='color: #d0d0d0; font-size: 1rem; line-height: 1.7; margin-bottom: 1.5rem;'>
            {paragraph}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Light comparison table
    st.dataframe(
        df_compare,
        use_container_width=True,
        hide_index=True
    )
    
    # FX implication
    st.markdown(f"""
    <div style='background: rgba(0, 166, 118, 0.1); 
                padding: 1rem 1.5rem; 
                border-radius: 8px; 
                border-left: 4px solid {fx_color};
                margin: 1rem 0 2rem 0;'>
        <div style='color: {fx_color}; font-weight: 600; font-size: 0.9rem;'>
            💱 FX IMPLICATION
        </div>
        <div style='color: #e0e0e0; font-size: 1rem; margin-top: 0.5rem;'>
            {fx_implication}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_collapsible_indicators(analysis_results, indicator_type, region, explore_mode=False):
    """
    Layer 3: Collapsible indicator groups with two-state cards
    - Collapsed by default (unless explore_mode is on)
    - Collapsed state: headline only
    - Expanded state: full detail
    """
    # Filter indicators
    filtered = [
        (k, v) for k, v in analysis_results.items()
        if v.get('indicator_type') == indicator_type 
        and v.get('region') == region
        and not v.get('hidden', False)
    ]
    
    if not filtered:
        return
    
    # Sort by name
    filtered.sort(key=lambda x: x[1].get('name', ''))
    
    # Determine icon
    icon_map = {
        'Leading': '📈',
        'Coincident': '📊',
        'Lagging': '📉'
    }
    icon = icon_map.get(indicator_type, '📊')
    
    # Create expander (expanded if explore_mode is on)
    with st.expander(f"{icon} **{indicator_type} Indicators** ({len(filtered)})", expanded=explore_mode):
        for series_id, result in filtered:
            # Two-state card
            name = result.get('name', 'Unknown')
            raw_value = result.get('current_value')
            formatted_value, custom_unit = format_indicator_value(series_id, raw_value)
            
            # Build value string
            if custom_unit:
                value_str = f"{formatted_value} {custom_unit}"
            else:
                is_inflation = result.get('is_inflation', False)
                if is_inflation:
                    value_str = f"{formatted_value}% YoY"
                else:
                    unit = result.get('unit', '')
                    value_str = f"{formatted_value} {unit}" if unit else str(formatted_value)
            
            percentile_all = result.get('percentile_all')
            trend_label = result.get('trend_label', 'Flat →')
            dynamic_line = result.get('dynamic_line', '')
            
            # Determine signal based on percentile
            if percentile_all is not None:
                if percentile_all > 70:
                    signal = "High"
                    signal_color = "#00ff80"
                elif percentile_all < 30:
                    signal = "Low"
                    signal_color = "#ff4444"
                else:
                    signal = "Mid-range"
                    signal_color = "#888888"
            else:
                signal = "N/A"
                signal_color = "#888888"
            
            # Collapsed state: Headline only
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"**{name}**")
                st.caption(f"{value_str} • {result.get('current_date', 'N/A')}")
            
            with col2:
                st.markdown(f"<div style='color: {signal_color}; font-weight: 600;'>{signal} → {trend_label}</div>", unsafe_allow_html=True)
            
            with col3:
                # Add a small "Details" button
                if st.button("📊 Details", key=f"expand_{series_id}_{indicator_type}", use_container_width=True):
                    st.session_state[f'show_detail_{series_id}'] = not st.session_state.get(f'show_detail_{series_id}', False)
            
            # Expanded state: Full detail (only if button clicked)
            if st.session_state.get(f'show_detail_{series_id}', False):
                st.markdown(f"""
                <div style='background: rgba(26, 31, 46, 0.5); padding: 1rem; border-radius: 8px; margin-top: 0.5rem; border-left: 3px solid {signal_color};'>
                    <div style='color: #d0d0d0; font-size: 0.9rem; margin-bottom: 0.5rem;'><strong>What it measures:</strong> {result.get('description', 'No description')}</div>
                    <div style='color: #d0d0d0; font-size: 0.9rem; margin-bottom: 0.5rem;'><strong>Current signal:</strong> {dynamic_line or 'No interpretation'}</div>
                    <div style='color: #d0d0d0; font-size: 0.9rem;'><strong>Why FX cares:</strong> Drives risk sentiment and growth expectations.</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show percentiles
                col_a, col_b = st.columns(2)
                with col_a:
                    color = get_percentile_color(percentile_all)
                    pct_display = f"{percentile_all}%" if percentile_all is not None else "N/A"
                    st.markdown(f"""
                    <div style='background-color: {color}; padding: 10px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 0.75rem; color: #000; font-weight: 700;'>ALL-TIME</div>
                        <div style='font-size: 1.1rem; font-weight: bold; color: #000; margin-top: 4px;'>{pct_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    percentile_recent = result.get('percentile_recent')
                    color = get_percentile_color(percentile_recent)
                    pct_display = f"{percentile_recent}%" if percentile_recent is not None else "N/A"
                    st.markdown(f"""
                    <div style='background-color: {color}; padding: 10px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 0.75rem; color: #000; font-weight: 700;'>5-YEAR</div>
                        <div style='font-size: 1.1rem; font-weight: bold; color: #000; margin-top: 4px;'>{pct_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show chart
                df = result.get('data')
                if df is not None and not df.empty:
                    df_recent = df.sort_values('date').tail(100)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_recent['date'],
                        y=df_recent['value'],
                        mode='lines',
                        line=dict(color='#0068c9', width=2),
                        showlegend=False
                    ))
                    fig.update_layout(
                        height=250,
                        margin=dict(l=40, r=40, t=20, b=40),
                        plot_bgcolor='#1a1f2e',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF'),
                        xaxis=dict(gridcolor='#2a2f3e'),
                        yaxis=dict(gridcolor='#2a2f3e')
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"detail_chart_{series_id}_{indicator_type}")
            
            st.markdown("---")

def main():
    st.title("🌍 Macro View")
    
    # Show loading status
    status_placeholder = st.empty()
    
    # Sidebar - Cache management
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Explore Mode Toggle
        st.markdown("**Display Mode:**")
        explore_mode = st.toggle("🔬 Explore Mode", value=False, help="Expand all indicator details by default")
        if explore_mode:
            st.caption("✅ All indicators expanded")
        else:
            st.caption("📖 Narrative-first view")
        
        st.markdown("---")
        
        # Cache info
        try:
            from cache_manager import CacheManager
            cache = CacheManager()
            cache_info = cache.get_cache_info()
            
            st.markdown("**Data Cache:**")
            st.caption(f"📦 {cache_info.get('num_datasets', 0)} datasets cached")
            st.caption(f"💾 {cache_info.get('total_size_mb', 0):.1f} MB")
            
            if st.button("🗑️ Clear Cache"):
                cache.clear_cache()
                st.success("Cache cleared!")
                st.rerun()
                
        except ImportError:
            st.caption("Cache not available")
        
        # Store explore_mode in session state for access in main
        st.session_state['explore_mode'] = explore_mode
    
    # Load all data with progress indicator
    import time
    start_time = time.time()
    
    status_placeholder.info('🔄 Loading 40 indicators (US + Eurozone)... First load: ~30-60 seconds. Cached loads: instant.')
    try:
        analysis_results, stale_indicators = load_all_data()
        load_time = time.time() - start_time
        status_placeholder.success(f'✅ Loaded {len(analysis_results)} indicators in {load_time:.1f} seconds')
        time.sleep(1)  # Show success message briefly
        status_placeholder.empty()  # Clear the loading message
                    
    except Exception as e:
        status_placeholder.error(f"Error loading data: {str(e)}")
        st.error("Full error:")
        import traceback
        st.code(traceback.format_exc())
        st.stop()
    
    # Show stale indicators warning if any
    if stale_indicators:
        with st.expander(f"⚠️ {len(stale_indicators)} indicators excluded (stale/unavailable data)"):
            st.caption("These indicators have data older than the frequency-based freshness threshold or are unavailable:")
            for item in sorted(stale_indicators):
                if isinstance(item, tuple):
                    name, last_date = item
                    st.caption(f"• {name} → Last: {last_date}")
                else:
                    st.caption(f"• {item}")
    
    # Region selector
    st.markdown("### Select Region")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🇺🇸 United States", use_container_width=True):
            st.session_state.selected_region = 'US'
    with col2:
        if st.button("🇪🇺 Eurozone", use_container_width=True):
            st.session_state.selected_region = 'Eurozone'
    
    # Initialize session state
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'US'
    
    selected_region = st.session_state.selected_region
    
    st.markdown(f"**Current View:** {selected_region}")
    st.markdown("---")
    
    # MACRO RELATIVE VIEW (US vs Eurozone comparison for FX context)
    create_macro_relative_view(analysis_results)
    
    st.markdown("---")
    
    # SINGLE REGION MODE
    flag_map = {
        "US": "🇺🇸",
        "Eurozone": "🇪🇺"
    }
    flag = flag_map.get(selected_region, "🌍")
    st.markdown(f"## {flag} {selected_region}")
    
    # Nikhil's Take - High-level commentary
    commentary_engine = CommentaryEngine()
    
    if selected_region == "US":
        nikhil_take = commentary_engine.generate_us_commentary(analysis_results)
        title = "🧠 Nikhil's Take — US Macro View"
    elif selected_region == "Eurozone":
        nikhil_take = commentary_engine.generate_eurozone_commentary(analysis_results)
        title = "🧠 Nikhil's Take — Eurozone Macro View"
    else:
        nikhil_take = None
        title = ""
    
    # LAYER 1: NARRATIVE (Always visible, dominant)
    if nikhil_take:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0a3d2e 0%, #0a0a0a 100%); 
                    padding: 2.5rem; 
                    border-radius: 16px; 
                    border: 3px solid #00ff80;
                    margin-bottom: 2rem;
                    box-shadow: 0 0 30px rgba(0,255,128,0.3);'>
            <div style='color: #00ff80; font-weight: 700; font-size: 1.5rem; margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 0.05em;'>
                {title}
            </div>
            <div style='color: #ffffff; font-size: 1.15rem; line-height: 1.8; font-weight: 400;'>
                {nikhil_take}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # LAYER 2: MACRO STATE SUMMARY (Scan layer)
    create_macro_state_summary(analysis_results, selected_region)
    
    st.markdown("---")
    
    # LAYER 3: INDICATOR EXPLORER (Optional, interactive)
    # Get explore mode from session state
    explore_mode = st.session_state.get('explore_mode', False)
    
    st.markdown("### 🔍 Indicator Explorer")
    if not explore_mode:
        st.caption("💡 Enable 'Explore Mode' in sidebar to auto-expand all indicators")
    
    # Collapsible indicator groups
    create_collapsible_indicators(analysis_results, 'Leading', selected_region, explore_mode)
    create_collapsible_indicators(analysis_results, 'Coincident', selected_region, explore_mode)
    create_collapsible_indicators(analysis_results, 'Lagging', selected_region, explore_mode)
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
