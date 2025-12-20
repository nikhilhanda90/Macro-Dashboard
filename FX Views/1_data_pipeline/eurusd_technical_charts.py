"""
EURUSD Technical Charts Generator
Creates candlestick chart with overlays and indicator panels
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import json

def create_technical_chart(df, fib_levels, summary):
    """
    Create comprehensive technical chart with:
    - Main panel: Candlesticks + MAs + Fib levels + 1Y high/low
    - Panel 2: RSI
    - Panel 3: MACD
    - Panel 4: Bollinger Width
    """
    
    # Take last 180 days for visual clarity
    df_chart = df.tail(180).copy()
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.15, 0.15],
        subplot_titles=('EURUSD Price & Key Levels', 'RSI (14)', 'MACD', 'Bollinger Width')
    )
    
    # =====================================================================
    # PANEL 1: CANDLESTICKS + MAs + FIB + LEVELS
    # =====================================================================
    
    # Candlesticks (primary visual)
    fig.add_trace(go.Candlestick(
        x=df_chart.index,
        open=df_chart['Open'],
        high=df_chart['High'],
        low=df_chart['Low'],
        close=df_chart['Close'],
        name='EURUSD',
        increasing=dict(line=dict(color='#00A676', width=1), fillcolor='rgba(0, 166, 118, 0.3)'),
        decreasing=dict(line=dict(color='#EF4444', width=1), fillcolor='rgba(239, 68, 68, 0.3)'),
    ), row=1, col=1)
    
    # Moving Averages (thin & muted)
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['SMA_50'],
        mode='lines',
        name='50d MA',
        line=dict(color='#3B82F6', width=1.5, dash='solid'),
        opacity=0.7
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['SMA_100'],
        mode='lines',
        name='100d MA',
        line=dict(color='#F59E0B', width=1.5, dash='dot'),
        opacity=0.7
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['SMA_200'],
        mode='lines',
        name='200d MA',
        line=dict(color='#8B5CF6', width=2, dash='solid'),
        opacity=0.8
    ), row=1, col=1)
    
    # Fibonacci levels (horizontal lines)
    fib_colors = {'38.2': '#FCD34D', '50.0': '#F59E0B', '61.8': '#F97316'}
    for fib_name in ['38.2', '50.0', '61.8']:
        if fib_name in fib_levels:
            fig.add_hline(
                y=fib_levels[fib_name],
                line_dash="dash",
                line_color=fib_colors[fib_name],
                line_width=1.5,
                opacity=0.6,
                annotation_text=f"Fib {fib_name}%",
                annotation_position="right",
                row=1, col=1
            )
    
    # 1-year high/low (dashed)
    year_high = df_chart['Year_High'].iloc[-1]
    year_low = df_chart['Year_Low'].iloc[-1]
    
    fig.add_hline(
        y=year_high,
        line_dash="dash",
        line_color="#EF4444",
        line_width=1,
        opacity=0.5,
        annotation_text="1Y High",
        annotation_position="left",
        row=1, col=1
    )
    
    fig.add_hline(
        y=year_low,
        line_dash="dash",
        line_color="#00A676",
        line_width=1,
        opacity=0.5,
        annotation_text="1Y Low",
        annotation_position="left",
        row=1, col=1
    )
    
    # =====================================================================
    # PANEL 2: RSI
    # =====================================================================
    
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='#00A676', width=2),
    ), row=2, col=1)
    
    # RSI levels (30, 50, 70)
    fig.add_hline(y=70, line_dash="dot", line_color="#EF4444", line_width=1, opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="#888888", line_width=1, opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#00A676", line_width=1, opacity=0.5, row=2, col=1)
    
    # =====================================================================
    # PANEL 3: MACD
    # =====================================================================
    
    # MACD line
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='#3B82F6', width=2),
    ), row=3, col=1)
    
    # Signal line
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['MACD_Signal'],
        mode='lines',
        name='Signal',
        line=dict(color='#F59E0B', width=1.5),
    ), row=3, col=1)
    
    # Histogram
    colors = ['#00A676' if val >= 0 else '#EF4444' for val in df_chart['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df_chart.index,
        y=df_chart['MACD_Hist'],
        name='Histogram',
        marker_color=colors,
        opacity=0.5
    ), row=3, col=1)
    
    # Zero line
    fig.add_hline(y=0, line_dash="dot", line_color="#888888", line_width=1, row=3, col=1)
    
    # =====================================================================
    # PANEL 4: BOLLINGER WIDTH
    # =====================================================================
    
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['BB_Width'],
        mode='lines',
        name='BB Width',
        line=dict(color='#8B5CF6', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)'
    ), row=4, col=1)
    
    # =====================================================================
    # LAYOUT
    # =====================================================================
    
    fig.update_layout(
        height=1200,
        plot_bgcolor='#1a1f2e',
        paper_bgcolor='#0f1419',
        font=dict(color='#FFFFFF', family='Arial', size=11),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(26, 31, 46, 0.8)',
            bordercolor='#3a4254',
            borderwidth=1
        ),
        xaxis4=dict(
            rangeslider=dict(visible=False),
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Update all y-axes
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')
    
    # Specific y-axis labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Width", row=4, col=1)
    
    return fig

def generate_charts():
    """Main function to generate technical charts"""
    print("="*80)
    print("GENERATING TECHNICAL CHARTS")
    print("="*80)
    
    # Load data
    data_path = Path(__file__).parent.parent / 'technical_outputs' / 'eurusd_technical_data.csv'
    summary_path = Path(__file__).parent.parent / 'technical_outputs' / 'eurusd_technical_summary.json'
    
    if not data_path.exists():
        print("❌ Technical data not found. Run eurusd_technicals.py first.")
        return
    
    print("\nLoading technical data...")
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    
    fib_levels = summary.get('fib_levels', {})
    
    print(f"✓ Loaded {len(df)} days of data")
    
    # Create chart
    print("\nCreating technical chart...")
    fig = create_technical_chart(df, fib_levels, summary)
    
    # Save
    output_path = Path(__file__).parent.parent / 'technical_outputs' / 'eurusd_technical_chart.html'
    fig.write_html(str(output_path))
    
    print(f"✓ Saved: {output_path}")
    
    # Also save as static image if kaleido is available
    try:
        img_path = Path(__file__).parent.parent / 'technical_outputs' / 'eurusd_technical_chart.png'
        fig.write_image(str(img_path), width=1400, height=1200)
        print(f"✓ Saved: {img_path}")
    except Exception as e:
        print(f"⚠️ Could not save PNG (kaleido not installed): {e}")
    
    print("\n" + "="*80)
    print("CHARTS GENERATED")
    print("="*80)

if __name__ == '__main__':
    generate_charts()

