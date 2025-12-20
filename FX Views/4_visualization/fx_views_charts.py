"""
FX Views Charts - 4 Core Visualizations
Generates publication-ready charts for website embedding
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import json
from pathlib import Path
from datetime import datetime

# Set style
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#0a0a0a'
plt.rcParams['axes.facecolor'] = '#0f0f0f'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.2

OUTPUT_DIR = Path('fx_views_outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

def load_data():
    """Load Layer 1 and Layer 2 data"""
    print("\n[LOADING DATA]")
    
    # Layer 1 (monthly)
    layer1_rec = json.load(open('fx_layer1_outputs/layer1_recommendation.json', 'r'))
    layer1_models = pd.read_pickle('fx_layer1_outputs/all_models.pkl')
    model_key = layer1_rec['selected_model']
    monthly_full = layer1_models[model_key]['monthly_full'].copy()
    sigma = layer1_rec['metrics']['sigma']
    
    print(f"  Layer 1: {len(monthly_full)} months ({model_key})")
    print(f"  Sigma: {sigma:.5f}")
    
    # Layer 2 (weekly)
    layer2_models = pd.read_pickle('fx_layer2_outputs/all_models.pkl')
    layer2_rec = json.load(open('fx_layer2_outputs/layer2_recommendation.json', 'r'))
    target = layer2_rec['target']
    model_key2 = layer2_rec['model_key']
    
    test_dates = pd.Series(layer2_models['test_dates'])
    test_z = layer2_models['test_z']
    test_pred = layer2_models[target][model_key2]['test_pred']
    
    # Compute actual delta_z from test_z
    actual_delta_z = np.diff(test_z, prepend=test_z[0])
    
    weekly_df = pd.DataFrame({
        'date': test_dates,
        'z_val': test_z,
        'delta_z_actual': actual_delta_z,
        'delta_z_pred': test_pred
    })
    
    print(f"  Layer 2: {len(weekly_df)} weeks ({model_key2})")
    
    return monthly_full, weekly_df, sigma

def chart1_fair_value_bands(monthly_full, sigma):
    """Chart 1: Fair Value & Regime Bands (Monthly)"""
    print("\n[CHART 1] Fair Value & Regime Bands...")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    dates = monthly_full['date']
    spot = monthly_full['spot']
    fv = monthly_full['fair_value']
    
    # Shaded bands (FV ± 1σ, FV ± 2σ)
    ax.fill_between(dates, fv - 2*sigma, fv + 2*sigma, 
                     alpha=0.15, color='#666666', label='±2σ (Break)')
    ax.fill_between(dates, fv - sigma, fv + sigma, 
                     alpha=0.25, color='#888888', label='±1σ (Stretch)')
    
    # Lines
    ax.plot(dates, spot, color='#00ff88', linewidth=2.5, label='Spot', zorder=5)
    ax.plot(dates, fv, color='#ff6b35', linewidth=2, label='Fair Value', linestyle='--', zorder=4)
    
    # Highlight Break months (|z| >= 2)
    break_mask = monthly_full['z_score'].abs() >= 2
    if break_mask.any():
        break_dates = monthly_full.loc[break_mask, 'date']
        break_spots = monthly_full.loc[break_mask, 'spot']
        ax.scatter(break_dates, break_spots, color='#ff3333', s=50, 
                   marker='o', zorder=6, label='Break Regime (|z| ≥ 2σ)')
    
    # Latest annotations
    latest = monthly_full.iloc[-1]
    latest_spot = latest['spot']
    latest_fv = latest['fair_value']
    latest_z = latest['z_score']
    latest_regime = latest['regime']
    
    # Annotation box (top-right)
    textstr = f"Latest ({latest['date'].strftime('%b %Y')})\n"
    textstr += f"Spot: {latest_spot:.4f}\n"
    textstr += f"Fair Value: {latest_fv:.4f}\n"
    textstr += f"Mispricing: {latest_z:+.2f}σ\n"
    textstr += f"Regime: {latest_regime}"
    
    props = dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, edgecolor='#00ff88')
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', bbox=props,
            family='monospace')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('EURUSD', fontsize=12)
    ax.set_title('Chart 1: Fair Value & Regime Bands (Monthly)', fontsize=14, pad=20)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'eurusd_fxviews_fair_value_monthly.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  [OK] Saved: {output_path}")

def chart2_mispricing_zscore(monthly_full):
    """Chart 2: Mispricing Z-Score Time Series (Monthly)"""
    print("\n[CHART 2] Mispricing Z-Score...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    dates = monthly_full['date']
    z = monthly_full['z_score']
    
    # Shaded regions
    ax.axhspan(-10, -2, color='#4a0000', alpha=0.15, label='Cheap Break (<-2σ)')
    ax.axhspan(-2, -1, color='#6b3300', alpha=0.15, label='Cheap Stretch (-2σ to -1σ)')
    ax.axhspan(-1, 1, color='#2a2a2a', alpha=0.15, label='Fair (-1σ to +1σ)')
    ax.axhspan(1, 2, color='#33336b', alpha=0.15, label='Rich Stretch (+1σ to +2σ)')
    ax.axhspan(2, 10, color='#4a004a', alpha=0.15, label='Rich Break (>+2σ)')
    
    # Horizontal reference lines
    for level in [-2, -1, 0, 1, 2]:
        ax.axhline(level, color='#666666', linewidth=0.8, linestyle='--', alpha=0.5)
    
    # Z-score line
    ax.plot(dates, z, color='#00ff88', linewidth=2.5, label='Mispricing Z-Score', zorder=5)
    ax.scatter(dates, z, color='#00ff88', s=20, alpha=0.6, zorder=6)
    
    # Latest value annotation
    latest_z = z.iloc[-1]
    latest_date = dates.iloc[-1]
    ax.scatter([latest_date], [latest_z], color='#ff3333', s=100, marker='D', 
               zorder=7, edgecolors='white', linewidths=1.5)
    ax.annotate(f'{latest_z:+.2f}σ', xy=(latest_date, latest_z), 
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, color='#ff3333', weight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', edgecolor='#ff3333'))
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Mispricing (σ)', fontsize=12)
    ax.set_title('Chart 2: Mispricing Z-Score Time Series (Monthly)', fontsize=14, pad=20)
    ax.set_ylim(-3.5, 3.5)
    ax.legend(loc='upper left', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'eurusd_fxviews_mispricing_z_monthly.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  [OK] Saved: {output_path}")

def chart3_weekly_pressure(weekly_df):
    """Chart 3: Weekly Pressure Panel (Δz actual vs predicted)"""
    print("\n[CHART 3] Weekly Pressure...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    dates = weekly_df['date']
    actual = weekly_df['delta_z_actual']
    pred = weekly_df['delta_z_pred']
    
    # Lines
    ax.plot(dates, actual, color='#00ccff', linewidth=2, label='Actual Δz', marker='o', markersize=4)
    ax.plot(dates, pred, color='#ff6b35', linewidth=2, label='Predicted Δz', marker='s', markersize=4)
    
    # Zero line
    ax.axhline(0, color='#666666', linewidth=1, linestyle='--', alpha=0.7)
    
    # Shading for positive/negative
    ax.fill_between(dates, 0, pred, where=(pred >= 0), alpha=0.2, color='#ff6b35', 
                     interpolate=True, label='Expanding Pressure')
    ax.fill_between(dates, 0, pred, where=(pred < 0), alpha=0.2, color='#00ff88', 
                     interpolate=True, label='Compressing Pressure')
    
    # Latest annotation
    latest = weekly_df.iloc[-1]
    latest_pred = latest['delta_z_pred']
    latest_date = latest['date']
    pressure_dir = "Compressing" if latest_pred < 0 else "Expanding"
    conf_label = "High" if abs(latest_pred) >= 0.3 else ("Med" if abs(latest_pred) >= 0.15 else "Low")
    
    textstr = f"Latest ({latest_date.strftime('%Y-%m-%d')})\n"
    textstr += f"Pressure: {pressure_dir}\n"
    textstr += f"Predicted Δz: {latest_pred:+.3f}\n"
    textstr += f"Confidence: {conf_label}"
    
    props = dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, edgecolor='#ff6b35')
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', bbox=props,
            family='monospace')
    
    ax.set_xlabel('Date (Weekly)', fontsize=12)
    ax.set_ylabel('Δz (Change in Mispricing)', fontsize=12)
    ax.set_title('Chart 3: Weekly Pressure Panel (Δz Actual vs Predicted)', fontsize=14, pad=20)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'eurusd_fxviews_pressure_weekly.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  [OK] Saved: {output_path}")

def chart4_decision_map(monthly_full, weekly_df):
    """Chart 4: Decision Map Scatter (Valuation vs Pressure)"""
    print("\n[CHART 4] Decision Map (Valuation × Pressure)...")
    
    # Map monthly z to weekly via forward fill for visualization
    monthly_z = monthly_full[['date', 'z_score']].copy()
    monthly_z['date'] = pd.to_datetime(monthly_z['date'])
    weekly_df['date'] = pd.to_datetime(weekly_df['date'])
    
    # Merge (forward fill monthly to weekly)
    weekly_with_z = pd.merge_asof(
        weekly_df.sort_values('date'),
        monthly_z.sort_values('date'),
        on='date',
        direction='backward'
    )
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    z_vals = weekly_with_z['z_score']
    delta_z_preds = weekly_with_z['delta_z_pred']
    
    # Quadrant lines
    ax.axvline(0, color='#666666', linewidth=1.5, linestyle='-', alpha=0.7)
    ax.axhline(0, color='#666666', linewidth=1.5, linestyle='-', alpha=0.7)
    ax.axvline(-1, color='#444444', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvline(1, color='#444444', linewidth=0.8, linestyle='--', alpha=0.5)
    
    # Scatter points
    scatter = ax.scatter(z_vals, delta_z_preds, c=range(len(z_vals)), 
                         cmap='plasma', s=50, alpha=0.6, edgecolors='white', linewidths=0.5)
    
    # Latest point (highlighted)
    latest_z = z_vals.iloc[-1]
    latest_dz = delta_z_preds.iloc[-1]
    latest_date = weekly_with_z['date'].iloc[-1]
    ax.scatter([latest_z], [latest_dz], color='#ff3333', s=300, marker='*', 
               zorder=10, edgecolors='white', linewidths=2)
    ax.annotate(f"Latest\n{latest_date.strftime('%Y-%m-%d')}", 
                xy=(latest_z, latest_dz), xytext=(15, 15), textcoords='offset points',
                fontsize=11, color='#ff3333', weight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', edgecolor='#ff3333'),
                arrowprops=dict(arrowstyle='->', color='#ff3333', lw=1.5))
    
    # Quadrant labels
    quad_props = dict(fontsize=11, style='italic', alpha=0.7, family='sans-serif')
    ax.text(-2, 0.8, 'Cheap +\nExpanding\n"Knife catch risk"', 
            ha='center', va='center', color='#ff6666', **quad_props)
    ax.text(-2, -0.8, 'Cheap +\nCompressing\n"Mean reversion\nunderway"', 
            ha='center', va='center', color='#66ff66', **quad_props)
    ax.text(2, 0.8, 'Rich +\nExpanding\n"Momentum\nvs value"', 
            ha='center', va='center', color='#ffcc66', **quad_props)
    ax.text(2, -0.8, 'Rich +\nCompressing\n"Overvaluation\nfading"', 
            ha='center', va='center', color='#66ccff', **quad_props)
    
    ax.set_xlabel('Valuation (Z-Score)', fontsize=13)
    ax.set_ylabel('Pressure (Predicted Δz)', fontsize=13)
    ax.set_title('Chart 4: Decision Map - Valuation × Pressure', fontsize=14, pad=20)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True, alpha=0.2)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label('Time Progression', fontsize=10)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'eurusd_fxviews_decision_map.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  [OK] Saved: {output_path}")

def main():
    print("="*80)
    print("FX VIEWS CHARTS GENERATION")
    print("="*80)
    
    # Load data
    monthly_full, weekly_df, sigma = load_data()
    
    # Generate 4 charts
    chart1_fair_value_bands(monthly_full, sigma)
    chart2_mispricing_zscore(monthly_full)
    chart3_weekly_pressure(weekly_df)
    chart4_decision_map(monthly_full, weekly_df)
    
    print("\n" + "="*80)
    print("[SUCCESS] All 4 charts generated!")
    print("="*80)
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
    print("\nFiles created:")
    print("  1. eurusd_fxviews_fair_value_monthly.png")
    print("  2. eurusd_fxviews_mispricing_z_monthly.png")
    print("  3. eurusd_fxviews_pressure_weekly.png")
    print("  4. eurusd_fxviews_decision_map.png")

if __name__ == "__main__":
    main()

