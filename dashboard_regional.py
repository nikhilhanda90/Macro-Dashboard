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
    - EA_EMPLOYMENT: thousands -> millions (167886 -> 167.9M)
    - EA_UNEMPLOYMENT: already percent (6.5 -> 6.5%)
    - Japan Exports/Imports: billions of yen -> trillions
    """
    if raw_value is None or pd.isna(raw_value):
        return "N/A", ""
    
    # Euro Area Employment Level (thousands → millions)
    if series_id == "EA_EMPLOYMENT":
        value_millions = raw_value / 1000.0
        return f"{value_millions:.1f}M", "persons"
    
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
                        # Custom formatting was applied (e.g., EA_EMPLOYMENT, EA_UNEMPLOYMENT)
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

def main():
    st.title("🌍 Macro View")
    
    # Show loading status
    status_placeholder = st.empty()
    
    # Sidebar - Cache management
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
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
    
    if nikhil_take:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0a3d2e 0%, #0a0a0a 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border: 2px solid #00ff80;
                    margin-bottom: 2rem;
                    box-shadow: 0 0 20px rgba(0,255,128,0.2);'>
            <div style='color: #00ff80; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.8rem;'>
                {title}
            </div>
            <div style='color: #ffffff; font-size: 1rem; line-height: 1.6;'>
                {nikhil_take}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary boxes
    create_summary_boxes(analysis_results, selected_region)
    
    st.markdown("---")
    
    # Leading Indicators
    st.markdown("## 📈 Leading Indicators (early signals)")
    create_indicator_cards(analysis_results, 'Leading', selected_region)
    
    # Coincident Indicators
    st.markdown("## 📊 Coincident Indicators (right now)")
    create_indicator_cards(analysis_results, 'Coincident', selected_region)
    
    # Lagging Indicators
    st.markdown("## 📉 Lagging Indicators (after the fact)")
    create_indicator_cards(analysis_results, 'Lagging', selected_region)
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

