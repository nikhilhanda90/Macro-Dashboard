"""
FX LAYER 2 - WEEKLY MACRO-FINANCIAL PRESSURE DATA
Build weekly dataset for pressure signal models

INCLUDED (Weekly frequency):
- US vs EA market yields (daily → weekly last)
- Credit spreads (daily → weekly last)
- Volatility: VIX, VXEEM (daily → weekly mean)
- Liquidity: Fed RRP (daily → weekly last)
- Optional: FX momentum features

EXCLUDED (Monthly macro):
- CPI/HICP (monthly releases)
- Unemployment (monthly releases)
- Other monthly macro indicators
"""
import pandas as pd
import numpy as np
from pathlib import Path
from data_fetcher import DataFetcher
import pickle
from datetime import datetime

print("="*80)
print("FX LAYER 2 - BUILDING WEEKLY PRESSURE DATASET")
print("="*80)
print("Purpose: Market-driven signals that move weekly")
print("="*80)

fetcher = DataFetcher()

# ============================================================================
# 1. DAILY MARKET SERIES → Weekly
# ============================================================================

print("\n[1] Fetching daily market series (convert to weekly)...")

daily_series_config = {
    # US Yields
    'DGS1': ('last', 'US 1Y Treasury'),
    'DGS2': ('last', 'US 2Y Treasury'),
    'DGS10': ('last', 'US 10Y Treasury'),
    'DFII10': ('last', 'US 10Y TIPS'),
    
    # US Curve
    'T10Y3M': ('last', 'US 10Y-3M Curve'),
    'T10Y2Y': ('last', 'US 10Y-2Y Curve'),
    
    # Credit Spreads
    'BAMLH0A0HYM2': ('last', 'US High Yield Spread'),
    'BAMLC0A4CBBB': ('last', 'US BBB Spread'),
    'BAMLHE00EHYIEY': ('last', 'EA High Yield Spread'),
    
    # Volatility (use mean for smoother weekly vol)
    'VIXCLS': ('mean', 'VIX'),
    'VXEEMCLS': ('mean', 'EM Volatility'),
    
    # Liquidity
    'RRPONTSYD': ('last', 'Fed Reverse Repo'),
    
    # FX Spot
    'DEXUSEU': ('last', 'EURUSD Spot'),
}

weekly_data = {}
for series_id, (agg_method, name) in daily_series_config.items():
    print(f"  Fetching {series_id:20s} ({name})...")
    try:
        df = fetcher.get_fred_series(series_id, years_back=20)
        if df is not None and not df.empty:
            series = df.set_index('date')['value']
            
            # Resample to weekly (Friday close, standard market convention)
            if agg_method == 'last':
                weekly_series = series.resample('W-FRI').last()
            elif agg_method == 'mean':
                weekly_series = series.resample('W-FRI').mean()
            else:
                weekly_series = series.resample('W-FRI').last()
            
            weekly_data[series_id] = weekly_series
            print(f"    ✓ {len(weekly_series)} weeks, latest: {weekly_series.index.max().strftime('%Y-%m-%d')}")
        else:
            print(f"    ✗ Failed")
    except Exception as e:
        print(f"    ✗ Error: {e}")

# ============================================================================
# 2. EA YIELDS FROM CSV → Weekly
# ============================================================================

print("\n[2] Loading EA yields from CSV (resample to weekly)...")

csv_path = Path('eurozone_data/ecb_yield_curve_full.csv')
if csv_path.exists():
    try:
        df_yields = pd.read_csv(csv_path)
        df_yields['TIME_PERIOD'] = pd.to_datetime(df_yields['TIME_PERIOD'])
        df_yields['OBS_VALUE'] = pd.to_numeric(df_yields['OBS_VALUE'], errors='coerce')
        
        # Extract key maturities
        ea_1y = df_yields[df_yields['maturity'].str.contains('1 year', case=False, na=False)]
        ea_2y = df_yields[df_yields['maturity'].str.contains('2 year', case=False, na=False)]
        ea_10y = df_yields[df_yields['maturity'].str.contains('10 year', case=False, na=False)]
        
        # Resample to weekly (last available in week)
        ea_1y_weekly = ea_1y.set_index('TIME_PERIOD')['OBS_VALUE'].resample('W-FRI').last()
        ea_2y_weekly = ea_2y.set_index('TIME_PERIOD')['OBS_VALUE'].resample('W-FRI').last()
        ea_10y_weekly = ea_10y.set_index('TIME_PERIOD')['OBS_VALUE'].resample('W-FRI').last()
        
        weekly_data['EA_1Y'] = ea_1y_weekly
        weekly_data['EA_2Y'] = ea_2y_weekly
        weekly_data['EA_10Y'] = ea_10y_weekly
        
        print(f"  ✓ EA yields: {len(ea_10y_weekly)} weeks")
        print(f"    Latest: {ea_10y_weekly.index.max().strftime('%Y-%m-%d')}, EA 10Y: {ea_10y_weekly.iloc[-1]:.2f}%")
    except Exception as e:
        print(f"  ✗ Error loading EA yields: {e}")
else:
    print(f"  ✗ CSV not found: {csv_path}")

# ============================================================================
# 3. COMBINE WEEKLY DATA
# ============================================================================

print("\n[3] Combining all weekly series...")

df_weekly = pd.DataFrame(weekly_data)
print(f"  Combined: {len(df_weekly)} weeks × {len(df_weekly.columns)} series")
print(f"  Date range: {df_weekly.index.min().strftime('%Y-%m-%d')} to {df_weekly.index.max().strftime('%Y-%m-%d')}")

# Check for missing data
print("\n  Missing data check:")
missing_counts = df_weekly.isnull().sum()
problem_cols = missing_counts[missing_counts > 0]
if not problem_cols.empty:
    print(f"  ⚠ Columns with NaN:")
    for col, count in problem_cols.items():
        pct = count / len(df_weekly) * 100
        print(f"    {col:30s} {count:4d} NaN ({pct:5.1f}%)")
else:
    print("  ✓ No NaN in any column")

# Drop rows with NaN in critical columns
critical_cols = ['DEXUSEU', 'DGS10', 'EA_10Y', 'VIXCLS']
initial_rows = len(df_weekly)
df_weekly = df_weekly.dropna(subset=[c for c in critical_cols if c in df_weekly.columns])
dropped = initial_rows - len(df_weekly)
if dropped > 0:
    print(f"  Dropped {dropped} weeks with missing critical data")

print(f"\n✓ Final weekly dataset: {len(df_weekly)} weeks × {len(df_weekly.columns)} series")

# Save raw weekly data
output_path = 'fx_layer2_weekly_raw.pkl'
with open(output_path, 'wb') as f:
    pickle.dump(df_weekly, f)
print(f"✓ Saved: {output_path}")

# ============================================================================
# SANITY CHECKS
# ============================================================================

print("\n" + "="*80)
print("SANITY CHECKS")
print("="*80)

# 1. Frequency check
print("\n[CHECK 1] Frequency is weekly?")
freq = df_weekly.index.inferred_freq
print(f"  Inferred frequency: {freq}")
if freq in ['W', 'W-FRI', None]:  # None is OK for irregular weekly
    print("  ✓ Weekly frequency confirmed")
else:
    print(f"  ⚠ Unexpected frequency: {freq}")

# 2. EA yields vary weekly
print("\n[CHECK 2] EA yields change weekly (not flat)?")
if 'EA_10Y' in df_weekly.columns:
    ea_10y_changes = df_weekly['EA_10Y'].diff().abs()
    zero_changes = (ea_10y_changes == 0).sum()
    total_weeks = len(ea_10y_changes) - 1
    print(f"  EA 10Y unchanged weeks: {zero_changes}/{total_weeks} ({zero_changes/total_weeks*100:.1f}%)")
    
    if zero_changes / total_weeks > 0.5:
        print("  ❌ EA 10Y is mostly flat - possible issue!")
    else:
        print("  ✓ EA 10Y shows weekly variation")
    
    # Show last 8 weeks
    print("\n  Last 8 weeks of EA 10Y:")
    print(df_weekly['EA_10Y'].tail(8).to_string())

# 3. VIX distribution
print("\n[CHECK 3] VIX distribution reasonable?")
if 'VIXCLS' in df_weekly.columns:
    vix_stats = df_weekly['VIXCLS'].describe(percentiles=[.1, .5, .9])
    print(f"  VIX statistics:")
    print(vix_stats.to_string())
    
    vix_high = (df_weekly['VIXCLS'] > 20).mean()
    print(f"\n  % weeks VIX > 20: {vix_high:.1%}")
    if 0.20 <= vix_high <= 0.40:
        print("  ✓ VIX distribution reasonable")
    else:
        print(f"  ⚠ VIX > 20 frequency: {vix_high:.1%} (expected 20-40%)")

# 4. EURUSD spot consistency
print("\n[CHECK 4] EURUSD spot looks consistent?")
if 'DEXUSEU' in df_weekly.columns:
    spot_stats = df_weekly['DEXUSEU'].describe()
    print(f"  EURUSD spot:")
    print(f"    Count:  {spot_stats['count']:.0f}")
    print(f"    Min:    {spot_stats['min']:.4f}")
    print(f"    Max:    {spot_stats['max']:.4f}")
    print(f"    Mean:   {spot_stats['mean']:.4f}")
    print(f"    Latest: {df_weekly['DEXUSEU'].iloc[-1]:.4f} ({df_weekly.index[-1].strftime('%Y-%m-%d')})")
    
    # Check for extreme weekly jumps
    weekly_jumps = df_weekly['DEXUSEU'].diff().abs()
    max_jump = weekly_jumps.max()
    if max_jump > 0.05:  # > 500 pips in a week is suspicious
        jump_date = weekly_jumps.idxmax()
        print(f"  ⚠ Max weekly jump: {max_jump:.4f} on {jump_date.strftime('%Y-%m-%d')}")
    else:
        print(f"  ✓ No suspicious jumps (max: {max_jump:.4f})")

# 5. Data frequency vs monthly
print("\n[CHECK 5] Weekly has more observations than monthly?")
print(f"  Weekly observations: {len(df_weekly)}")
expected_monthly = len(df_weekly) / 4.33  # ~4.33 weeks per month
print(f"  Expected monthly: ~{expected_monthly:.0f}")
print(f"  ✓ Weekly provides ~4.3x more granularity")

print("\n" + "="*80)
print("✅ WEEKLY DATASET BUILD COMPLETE")
print("="*80)
print(f"\nNext step: Run 'fx_layer2_weekly_features.py' to engineer pressure features")


