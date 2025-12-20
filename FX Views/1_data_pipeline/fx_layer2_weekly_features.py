"""
FX LAYER 2 - WEEKLY FEATURE ENGINEERING
Engineer pressure features from weekly market data

Focus: Market-driven signals that move weekly (not monthly macro)
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

print("="*80)
print("FX LAYER 2 - WEEKLY FEATURE ENGINEERING")
print("="*80)

# Load weekly raw data
with open('fx_layer2_weekly_raw.pkl', 'rb') as f:
    df_weekly = pickle.load(f)

print(f"\n✓ Loaded weekly data: {df_weekly.shape}")
print(f"  Date range: {df_weekly.index.min().strftime('%Y-%m-%d')} to {df_weekly.index.max().strftime('%Y-%m-%d')}")

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

print("\n[STEP 1] Engineering pressure features...")

features = pd.DataFrame(index=df_weekly.index)

# -----------------------------------------------------------------------------
# 1. RATE DIFFERENTIALS
# -----------------------------------------------------------------------------
print("\n[1] Rate differentials (US - EA)...")

# 1Y differential
if 'DGS1' in df_weekly.columns and 'EA_1Y' in df_weekly.columns:
    features['rate_1Y_diff'] = df_weekly['DGS1'] - df_weekly['EA_1Y']
    print(f"  ✓ rate_1Y_diff")

# 2Y differential
if 'DGS2' in df_weekly.columns and 'EA_2Y' in df_weekly.columns:
    features['rate_2Y_diff'] = df_weekly['DGS2'] - df_weekly['EA_2Y']
    print(f"  ✓ rate_2Y_diff")

# 10Y differential
if 'DGS10' in df_weekly.columns and 'EA_10Y' in df_weekly.columns:
    features['rate_10Y_diff'] = df_weekly['DGS10'] - df_weekly['EA_10Y']
    print(f"  ✓ rate_10Y_diff")

# Real rate (US TIPS)
if 'DFII10' in df_weekly.columns:
    features['US_real_rate'] = df_weekly['DFII10']
    print(f"  ✓ US_real_rate")

# -----------------------------------------------------------------------------
# 2. YIELD CURVES
# -----------------------------------------------------------------------------
print("\n[2] Yield curves...")

# US curves
if 'T10Y3M' in df_weekly.columns:
    features['US_curve_10Y3M'] = df_weekly['T10Y3M']
    print(f"  ✓ US_curve_10Y3M")

if 'T10Y2Y' in df_weekly.columns:
    features['US_curve_10Y2Y'] = df_weekly['T10Y2Y']
    print(f"  ✓ US_curve_10Y2Y")

# EA curve (construct from individual yields)
if 'EA_10Y' in df_weekly.columns and 'EA_1Y' in df_weekly.columns:
    features['EA_curve_10Y1Y'] = df_weekly['EA_10Y'] - df_weekly['EA_1Y']
    print(f"  ✓ EA_curve_10Y1Y")

if 'EA_10Y' in df_weekly.columns and 'EA_2Y' in df_weekly.columns:
    features['EA_curve_10Y2Y'] = df_weekly['EA_10Y'] - df_weekly['EA_2Y']
    print(f"  ✓ EA_curve_10Y2Y")

# -----------------------------------------------------------------------------
# 3. CREDIT SPREADS
# -----------------------------------------------------------------------------
print("\n[3] Credit spreads...")

# US spreads (levels)
if 'BAMLH0A0HYM2' in df_weekly.columns:
    features['US_HY_spread'] = df_weekly['BAMLH0A0HYM2']
    print(f"  ✓ US_HY_spread")

if 'BAMLC0A4CBBB' in df_weekly.columns:
    features['US_BBB_spread'] = df_weekly['BAMLC0A4CBBB']
    print(f"  ✓ US_BBB_spread")

# EA spreads
if 'BAMLHE00EHYIEY' in df_weekly.columns:
    features['EA_HY_spread'] = df_weekly['BAMLHE00EHYIEY']
    print(f"  ✓ EA_HY_spread")

# Credit differential (US - EA)
if 'BAMLH0A0HYM2' in df_weekly.columns and 'BAMLHE00EHYIEY' in df_weekly.columns:
    features['HY_spread_diff'] = df_weekly['BAMLH0A0HYM2'] - df_weekly['BAMLHE00EHYIEY']
    print(f"  ✓ HY_spread_diff (US - EA)")

# -----------------------------------------------------------------------------
# 4. VOLATILITY
# -----------------------------------------------------------------------------
print("\n[4] Volatility...")

if 'VIXCLS' in df_weekly.columns:
    features['VIX'] = df_weekly['VIXCLS']
    print(f"  ✓ VIX")

if 'VXEEMCLS' in df_weekly.columns:
    features['VXEEM'] = df_weekly['VXEEMCLS']
    print(f"  ✓ VXEEM")

# VIX regime (high vol = VIX > 20)
if 'VIXCLS' in df_weekly.columns:
    features['VIX_high'] = (df_weekly['VIXCLS'] > 20).astype(int)
    print(f"  ✓ VIX_high (regime)")

# -----------------------------------------------------------------------------
# 5. LIQUIDITY
# -----------------------------------------------------------------------------
print("\n[5] Liquidity...")

if 'RRPONTSYD' in df_weekly.columns:
    features['RRP'] = df_weekly['RRPONTSYD']
    # Normalize by billions
    features['RRP_bn'] = features['RRP'] / 1000.0
    print(f"  ✓ RRP_bn (billions)")

# -----------------------------------------------------------------------------
# 6. FX MOMENTUM
# -----------------------------------------------------------------------------
print("\n[6] FX momentum features...")

if 'DEXUSEU' in df_weekly.columns:
    spot = df_weekly['DEXUSEU']
    
    # Weekly returns
    features['fx_ret_1w'] = spot.pct_change(1) * 100
    features['fx_ret_4w'] = spot.pct_change(4) * 100
    features['fx_ret_12w'] = spot.pct_change(12) * 100
    
    # Moving averages
    features['fx_ma4'] = spot.rolling(4).mean()
    features['fx_ma12'] = spot.rolling(12).mean()
    features['fx_ma26'] = spot.rolling(26).mean()
    
    # MA crosses
    features['fx_ma4_cross'] = (features['fx_ma4'] > features['fx_ma12']).astype(int)
    features['fx_ma12_cross'] = (features['fx_ma12'] > features['fx_ma26']).astype(int)
    
    # Rolling volatility (4-week std of weekly returns)
    features['fx_vol_4w'] = spot.pct_change().rolling(4).std() * 100
    
    print(f"  ✓ fx_ret_1w, fx_ret_4w, fx_ret_12w")
    print(f"  ✓ fx_ma4, fx_ma12, fx_ma26")
    print(f"  ✓ fx_ma_crosses, fx_vol_4w")

print(f"\n✓ Created {len(features.columns)} base features")

# ============================================================================
# TRANSFORM VARIANTS (Lags & Changes)
# ============================================================================

print("\n[STEP 2] Generating transform variants (lags, changes)...")

final_features = pd.DataFrame(index=df_weekly.index)

for col in features.columns:
    # Skip already-lagged features (ma_cross, etc)
    if col.startswith('fx_ma') or col.endswith('_cross') or col.endswith('_high'):
        final_features[f'{col}_t'] = features[col]
        continue
    
    # Level (_t)
    final_features[f'{col}_t'] = features[col]
    
    # Lags (t-1, t-2, t-4 weeks)
    final_features[f'{col}_t1'] = features[col].shift(1)
    final_features[f'{col}_t2'] = features[col].shift(2)
    final_features[f'{col}_t4'] = features[col].shift(4)
    
    # Weekly changes
    final_features[f'd1w_{col}'] = features[col].diff(1)
    final_features[f'd4w_{col}'] = features[col].diff(4)
    
    # 12-week rolling Z-score
    rolling_mean = features[col].rolling(window=12).mean()
    rolling_std = features[col].rolling(window=12).std()
    final_features[f'z12w_{col}'] = (features[col] - rolling_mean) / rolling_std

print(f"✓ Engineered {len(final_features.columns)} total features (with transforms)")

# Add target (EURUSD spot)
if 'DEXUSEU' in df_weekly.columns:
    final_features['spot'] = df_weekly['DEXUSEU']
    print(f"✓ Added target: spot (EURUSD)")

# Drop rows with NaN (from lags and rolling windows)
initial_rows = len(final_features)
final_features = final_features.dropna()
dropped = initial_rows - len(final_features)
print(f"\n✓ Dropped {dropped} weeks with NaN (from lags/rolling)")
print(f"✓ Final feature set: {len(final_features)} weeks × {len(final_features.columns)} features")

# ============================================================================
# SAVE
# ============================================================================

output_path = 'fx_layer2_weekly_features.pkl'
with open(output_path, 'wb') as f:
    pickle.dump(final_features, f)
print(f"\n✓ Saved: {output_path}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("WEEKLY FEATURE ENGINEERING SUMMARY")
print("="*80)

print(f"\nDataset shape: {final_features.shape}")
print(f"Date range: {final_features.index.min().strftime('%Y-%m-%d')} to {final_features.index.max().strftime('%Y-%m-%d')}")

print(f"\nFeature categories:")
level_cols = [c for c in final_features.columns if c.endswith('_t')]
lag_cols = [c for c in final_features.columns if '_t1' in c or '_t2' in c or '_t4' in c]
change_cols = [c for c in final_features.columns if c.startswith('d1w_') or c.startswith('d4w_')]
z_cols = [c for c in final_features.columns if c.startswith('z12w_')]

print(f"  Levels:       {len(level_cols)}")
print(f"  Lags:         {len(lag_cols)}")
print(f"  Changes:      {len(change_cols)}")
print(f"  Z-scores:     {len(z_cols)}")
print(f"  Target:       1 (spot)")
print(f"  Total:        {len(final_features.columns)}")

print(f"\nLast 5 weeks:")
sample_cols = ['spot', 'rate_10Y_diff_t', 'US_HY_spread_t', 'VIX_t', 'fx_ret_4w_t']
available_cols = [c for c in sample_cols if c in final_features.columns]
print(final_features[available_cols].tail(5).to_string())

print("\n" + "="*80)
print("✅ WEEKLY FEATURE ENGINEERING COMPLETE")
print("="*80)
print(f"\nNext step: Run 'fx_layer2_pressure_model.py' to train weekly pressure models")


