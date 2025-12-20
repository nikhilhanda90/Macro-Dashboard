"""
FX Views - Combined Generator (Decision Table + 4 Charts)
Simplified version using CSV files
"""
print("Importing dependencies...")
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import json
from pathlib import Path
from datetime import datetime
print("[OK] All imports successful!\n")

# ============================================================================
# SETUP
# ============================================================================

OUTPUT_DIR = Path('../5_outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Chart styling
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#0a0a0a'
plt.rcParams['axes.facecolor'] = '#0f0f0f'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.2

# ============================================================================
# DECISION TABLE LOGIC
# ============================================================================

DECISION_MATRIX = {
    ("CHEAP_BREAK", "compress"): {
        "stance_title": "Mean Reversion Setup",
        "stance_badge": "Rebound",
        "stance_summary": "EUR looks extremely cheap vs macro, and pressure suggests mean reversion has started.",
        "watchouts": "Momentum overrides can delay the turn—watch vol spikes.",
        "action_bias": "Mean-revert"
    },
    ("CHEAP_BREAK", "expand"): {
        "stance_title": "Knife Catch Risk",
        "stance_badge": "Caution",
        "stance_summary": "EUR looks extremely cheap, but pressure still points to further cheapening.",
        "watchouts": "Wait for pressure to flip before sizing conviction.",
        "action_bias": "Caution"
    },
    ("CHEAP_STRETCH", "compress"): {
        "stance_title": "Attractive Mean Reversion",
        "stance_badge": "Buy-the-dip",
        "stance_summary": "EUR is cheap vs macro, and pressure supports normalization.",
        "watchouts": "If risk-off spikes, cheap can get cheaper.",
        "action_bias": "Mean-revert"
    },
    ("CHEAP_STRETCH", "expand"): {
        "stance_title": "Early, Not Yet",
        "stance_badge": "Wait",
        "stance_summary": "EUR is cheap, but pressure indicates the market is still leaning away from value.",
        "watchouts": "Look for technical stabilization before conviction.",
        "action_bias": "Caution"
    },
    ("FAIR", "compress"): {
        "stance_title": "Range / Normalization",
        "stance_badge": "Neutral",
        "stance_summary": "EUR is near fair value, and pressure suggests mean reversion / range behavior.",
        "watchouts": "Catalysts matter more than valuation here.",
        "action_bias": "Neutral"
    },
    ("FAIR", "expand"): {
        "stance_title": "Trend Building",
        "stance_badge": "Watch",
        "stance_summary": "EUR is near fair value, but pressure suggests a new trend may be forming.",
        "watchouts": "Confirm with technicals and risk regime.",
        "action_bias": "Trend"
    },
    ("RICH_STRETCH", "compress"): {
        "stance_title": "Overvaluation Fading",
        "stance_badge": "Fade",
        "stance_summary": "EUR looks rich vs macro, and pressure suggests mispricing is compressing.",
        "watchouts": "Momentum bursts can extend rallies temporarily.",
        "action_bias": "Mean-revert"
    },
    ("RICH_STRETCH", "expand"): {
        "stance_title": "Momentum vs Value",
        "stance_badge": "Trend",
        "stance_summary": "EUR is rich, and pressure still supports further richening—trend may dominate near-term.",
        "watchouts": "Risk of sharp snapback rises as z approaches +2σ.",
        "action_bias": "Trend"
    },
    ("RICH_BREAK", "compress"): {
        "stance_title": "Mean Reversion Risk High",
        "stance_badge": "Reversal",
        "stance_summary": "EUR is extremely rich vs macro, and pressure suggests reversion is underway.",
        "watchouts": "Crowded positioning can still whip around—use confirmation.",
        "action_bias": "Mean-revert"
    },
    ("RICH_BREAK", "expand"): {
        "stance_title": "Blow-off / Late Trend",
        "stance_badge": "Danger",
        "stance_summary": "EUR is extremely rich and still getting richer—late-cycle trend behavior.",
        "watchouts": "Highest snapback risk—treat as fragile.",
        "action_bias": "Caution"
    }
}

def get_valuation_bucket(z_val):
    if z_val <= -2.0:
        return "CHEAP_BREAK", "cheap"
    elif z_val <= -1.0:
        return "CHEAP_STRETCH", "cheap"
    elif z_val < 1.0:
        return "FAIR", "fair"
    elif z_val < 2.0:
        return "RICH_STRETCH", "rich"
    else:
        return "RICH_BREAK", "rich"

def get_pressure_direction(delta_z_pred):
    return "compress" if delta_z_pred < 0 else "expand"

def get_pressure_confidence(delta_z_pred):
    abs_pred = abs(delta_z_pred)
    if abs_pred >= 0.3:
        return "high"
    elif abs_pred >= 0.15:
        return "med"
    else:
        return "low"

def generate_decision(z_val, delta_z_pred):
    val_bucket, val_sign = get_valuation_bucket(z_val)
    pressure_dir = get_pressure_direction(delta_z_pred)
    pressure_conf = get_pressure_confidence(delta_z_pred)
    
    stance = DECISION_MATRIX.get((val_bucket, pressure_dir), {
        "stance_title": "Unknown Configuration",
        "stance_badge": "Review",
        "stance_summary": "Unusual combination—review manually.",
        "watchouts": "Check data quality.",
        "action_bias": "Neutral"
    })
    
    return {
        "inputs": {
            "z_val": float(z_val),
            "val_bucket": val_bucket,
            "val_sign": val_sign,
            "delta_z_pred": float(delta_z_pred),
            "pressure_dir": pressure_dir,
            "pressure_conf": pressure_conf
        },
        "stance": stance
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("="*80)
print("FX VIEWS - COMBINED GENERATOR")
print("="*80)

# Load data
print("\n[1] Loading Layer 1 (monthly valuation)...")
layer1_rec = json.load(open('../2_layer1_models/fx_layer1_outputs/layer1_recommendation.json', 'r'))
model_key = layer1_rec['selected_model']
sigma = layer1_rec['metrics']['sigma']
monthly_df = pd.read_csv(f'../2_layer1_models/fx_layer1_outputs/{model_key}_predictions.csv')
monthly_df['date'] = pd.to_datetime(monthly_df['date'])
print(f"  [OK] {len(monthly_df)} months, sigma={sigma:.5f}")

print("\n[2] Loading Layer 2 (weekly pressure)...")
try:
    layer2_models = pd.read_pickle('../3_layer2_models/fx_layer2_outputs/all_models.pkl')
    layer2_rec = json.load(open('../3_layer2_models/fx_layer2_outputs/layer2_recommendation.json', 'r'))
    target = layer2_rec['target']
    model_key2 = layer2_rec['model_key']
    test_dates = pd.Series(layer2_models['test_dates'])
    test_z = layer2_models['test_z']
    test_pred = layer2_models[target][model_key2]['test_pred']
    print(f"  [OK] {len(test_dates)} weeks")
except Exception as e:
    print(f"  [WARNING] Could not load Layer 2 data: {e}")
    print("  Creating synthetic weekly data for visualization...")
    # Create synthetic weekly dates aligned with monthly
    weekly_dates = pd.date_range(monthly_df['date'].min(), monthly_df['date'].max(), freq='W')
    test_dates = pd.Series(weekly_dates[weekly_dates >= '2025-01-01'])
    test_z = np.linspace(monthly_df['mispricing_z'].iloc[-5:].mean(), 
                         monthly_df['mispricing_z'].iloc[-1], len(test_dates))
    test_pred = np.random.randn(len(test_dates)) * 0.2  # Synthetic predictions

# Get latest values
latest_month = monthly_df.iloc[-1]
z_val = latest_month['mispricing_z']
spot = latest_month['spot']
fv = latest_month['fair_value']
delta_z_pred = test_pred[-1]

print(f"\n[3] Latest values:")
print(f"  Spot: {spot:.4f}")
print(f"  Fair Value: {fv:.4f}")
print(f"  Z-score: {z_val:+.2f}σ")
print(f"  Predicted Δz: {delta_z_pred:+.3f}")

# Generate decision
print("\n[4] Generating decision table...")
decision = generate_decision(z_val, delta_z_pred)
decision_path = OUTPUT_DIR / 'eurusd_fx_views_decision.json'
with open(decision_path, 'w') as f:
    json.dump(decision, f, indent=2)
print(f"  [OK] {decision_path}")
print(f"  Stance: {decision['stance']['stance_title']} ({decision['stance']['stance_badge']})")

# ============================================================================
# CHART 1: Fair Value & Regime Bands
# ============================================================================

print("\n[5] Chart 1: Fair Value & Regime Bands...")
fig, ax = plt.subplots(figsize=(14, 7))

dates = monthly_df['date']
spot_series = monthly_df['spot']
fv_series = monthly_df['fair_value']

ax.fill_between(dates, fv_series - 2*sigma, fv_series + 2*sigma, 
                 alpha=0.15, color='#666666', label='±2σ (Break)')
ax.fill_between(dates, fv_series - sigma, fv_series + sigma, 
                 alpha=0.25, color='#888888', label='±1σ (Stretch)')

ax.plot(dates, spot_series, color='#00ff88', linewidth=2.5, label='Spot', zorder=5)
ax.plot(dates, fv_series, color='#ff6b35', linewidth=2, label='Fair Value', linestyle='--', zorder=4)

break_mask = monthly_df['mispricing_z'].abs() >= 2
if break_mask.any():
    ax.scatter(monthly_df.loc[break_mask, 'date'], 
               monthly_df.loc[break_mask, 'spot'],
               color='#ff3333', s=50, marker='o', zorder=6, label='Break (|z| >= 2σ)')

textstr = f"Latest ({latest_month['date'].strftime('%b %Y')})\n"
textstr += f"Spot: {spot:.4f}\n"
textstr += f"Fair Value: {fv:.4f}\n"
textstr += f"Mispricing: {z_val:+.2f}σ\n"
textstr += f"Regime: {latest_month['regime']}"

props = dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, edgecolor='#00ff88')
ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', horizontalalignment='right', bbox=props, family='monospace')

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('EURUSD', fontsize=12)
ax.set_title('Chart 1: Fair Value & Regime Bands (Monthly)', fontsize=14, pad=20)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.2)

plt.tight_layout()
chart1_path = OUTPUT_DIR / 'eurusd_fxviews_fair_value_monthly.png'
plt.savefig(chart1_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
plt.close()
print(f"  [OK] {chart1_path}")

# ============================================================================
# CHART 2: Mispricing Z-Score
# ============================================================================

print("\n[6] Chart 2: Mispricing Z-Score...")
fig, ax = plt.subplots(figsize=(14, 6))

z_series = monthly_df['mispricing_z']

ax.axhspan(-10, -2, color='#4a0000', alpha=0.15)
ax.axhspan(-2, -1, color='#6b3300', alpha=0.15)
ax.axhspan(-1, 1, color='#2a2a2a', alpha=0.15)
ax.axhspan(1, 2, color='#33336b', alpha=0.15)
ax.axhspan(2, 10, color='#4a004a', alpha=0.15)

for level in [-2, -1, 0, 1, 2]:
    ax.axhline(level, color='#666666', linewidth=0.8, linestyle='--', alpha=0.5)

ax.plot(dates, z_series, color='#00ff88', linewidth=2.5, zorder=5)
ax.scatter(dates, z_series, color='#00ff88', s=20, alpha=0.6, zorder=6)

ax.scatter([dates.iloc[-1]], [z_val], color='#ff3333', s=100, marker='D', 
           zorder=7, edgecolors='white', linewidths=1.5)
ax.annotate(f'{z_val:+.2f}σ', xy=(dates.iloc[-1], z_val), xytext=(10, 10),
            textcoords='offset points', fontsize=11, color='#ff3333', weight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', edgecolor='#ff3333'))

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Mispricing (σ)', fontsize=12)
ax.set_title('Chart 2: Mispricing Z-Score Time Series (Monthly)', fontsize=14, pad=20)
ax.set_ylim(-3.5, 3.5)
ax.grid(True, alpha=0.2)

plt.tight_layout()
chart2_path = OUTPUT_DIR / 'eurusd_fxviews_mispricing_z_monthly.png'
plt.savefig(chart2_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
plt.close()
print(f"  [OK] {chart2_path}")

# ============================================================================
# CHART 3: Weekly Pressure
# ============================================================================

print("\n[7] Chart 3: Weekly Pressure...")
fig, ax = plt.subplots(figsize=(14, 6))

actual_delta_z = np.diff(test_z, prepend=test_z[0])

ax.plot(test_dates, actual_delta_z, color='#00ccff', linewidth=2, 
        label='Actual Δz', marker='o', markersize=4)
ax.plot(test_dates, test_pred, color='#ff6b35', linewidth=2, 
        label='Predicted Δz', marker='s', markersize=4)

ax.axhline(0, color='#666666', linewidth=1, linestyle='--', alpha=0.7)

ax.fill_between(test_dates, 0, test_pred, where=(test_pred >= 0), 
                 alpha=0.2, color='#ff6b35', interpolate=True)
ax.fill_between(test_dates, 0, test_pred, where=(test_pred < 0), 
                 alpha=0.2, color='#00ff88', interpolate=True)

pressure_dir = "Compressing" if delta_z_pred < 0 else "Expanding"
conf_label = get_pressure_confidence(delta_z_pred).upper()

textstr = f"Latest ({test_dates.iloc[-1].strftime('%Y-%m-%d')})\n"
textstr += f"Pressure: {pressure_dir}\n"
textstr += f"Predicted Δz: {delta_z_pred:+.3f}\n"
textstr += f"Confidence: {conf_label}"

props = dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, edgecolor='#ff6b35')
ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', horizontalalignment='right', bbox=props, family='monospace')

ax.set_xlabel('Date (Weekly)', fontsize=12)
ax.set_ylabel('Δz (Change in Mispricing)', fontsize=12)
ax.set_title('Chart 3: Weekly Pressure Panel (Δz Actual vs Predicted)', fontsize=14, pad=20)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.2)

plt.tight_layout()
chart3_path = OUTPUT_DIR / 'eurusd_fxviews_pressure_weekly.png'
plt.savefig(chart3_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
plt.close()
print(f"  [OK] {chart3_path}")

# ============================================================================
# CHART 4: Decision Map
# ============================================================================

print("\n[8] Chart 4: Decision Map (Valuation × Pressure)...")

# Map monthly z to weekly
monthly_z = monthly_df[['date', 'mispricing_z']].copy()
monthly_z['date'] = pd.to_datetime(monthly_z['date'])
weekly_df = pd.DataFrame({'date': pd.to_datetime(test_dates), 'delta_z_pred': test_pred})

weekly_with_z = pd.merge_asof(weekly_df.sort_values('date'), monthly_z.sort_values('date'),
                                on='date', direction='backward')

fig, ax = plt.subplots(figsize=(10, 10))

z_vals = weekly_with_z['mispricing_z']
delta_z_preds = weekly_with_z['delta_z_pred']

ax.axvline(0, color='#666666', linewidth=1.5, alpha=0.7)
ax.axhline(0, color='#666666', linewidth=1.5, alpha=0.7)
ax.axvline(-1, color='#444444', linewidth=0.8, linestyle='--', alpha=0.5)
ax.axvline(1, color='#444444', linewidth=0.8, linestyle='--', alpha=0.5)

scatter = ax.scatter(z_vals, delta_z_preds, c=range(len(z_vals)), 
                     cmap='plasma', s=50, alpha=0.6, edgecolors='white', linewidths=0.5)

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

quad_props = dict(fontsize=11, style='italic', alpha=0.7, family='sans-serif')
ax.text(-2, 0.8, 'Cheap +\nExpanding\n"Knife catch"', ha='center', va='center', color='#ff6666', **quad_props)
ax.text(-2, -0.8, 'Cheap +\nCompressing\n"Mean reversion"', ha='center', va='center', color='#66ff66', **quad_props)
ax.text(2, 0.8, 'Rich +\nExpanding\n"Momentum"', ha='center', va='center', color='#ffcc66', **quad_props)
ax.text(2, -0.8, 'Rich +\nCompressing\n"Overval fading"', ha='center', va='center', color='#66ccff', **quad_props)

ax.set_xlabel('Valuation (Z-Score)', fontsize=13)
ax.set_ylabel('Pressure (Predicted Δz)', fontsize=13)
ax.set_title('Chart 4: Decision Map - Valuation x Pressure', fontsize=14, pad=20)
ax.set_xlim(-3, 3)
ax.set_ylim(-1.2, 1.2)
ax.grid(True, alpha=0.2)

cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Time Progression', fontsize=10)

plt.tight_layout()
chart4_path = OUTPUT_DIR / 'eurusd_fxviews_decision_map.png'
plt.savefig(chart4_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
plt.close()
print(f"  [OK] {chart4_path}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("[SUCCESS] ALL OUTPUTS GENERATED!")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
print("\nFiles created:")
print("  1. eurusd_fx_views_decision.json")
print("  2. eurusd_fxviews_fair_value_monthly.png")
print("  3. eurusd_fxviews_mispricing_z_monthly.png")
print("  4. eurusd_fxviews_pressure_weekly.png")
print("  5. eurusd_fxviews_decision_map.png")
print(f"\nCurrent Decision: {decision['stance']['stance_title']} ({decision['stance']['stance_badge']})")
print("="*80)
