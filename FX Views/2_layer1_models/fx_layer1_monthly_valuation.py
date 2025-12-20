"""
FX LAYER 1 - MONTHLY MACRO VALUATION
Tests multiple model approaches and evaluates on proper criteria:
  1. Stability and interpretability of fair value
  2. Reasonable regime frequency  
  3. Economic coherence of features
  4. RMSE (secondary)
  5. R² (informational only)
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from pathlib import Path

print("="*80)
print("FX LAYER 1 - MONTHLY MACRO VALUATION MODEL")
print("="*80)
print("Purpose: Find stable macro anchor for fair value")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n[1] Loading monthly features...")
with open('eurusd_v2_monthly_features.pkl', 'rb') as f:
    df = pickle.load(f)

print(f"  Loaded: {df.shape[0]} months, {df.shape[1]-1} features + target")
print(f"  Range: {df.index.min().strftime('%Y-%m')} to {df.index.max().strftime('%Y-%m')}")

# ============================================================================
# TRAIN/TEST SPLIT
# ============================================================================

print("\n[2] Train/Test split...")

TRAIN_END = '2024-12-31'
train_df = df[df.index <= TRAIN_END]
test_df = df[df.index > TRAIN_END]

X_train = train_df.drop('spot', axis=1)
y_train = train_df['spot']
X_test = test_df.drop('spot', axis=1)
y_test = test_df['spot']

X_full = df.drop('spot', axis=1)
y_full = df['spot']

print(f"  Train: {len(X_train)} months (to {TRAIN_END})")
print(f"  Test:  {len(X_test)} months ({test_df.index.min().strftime('%Y-%m')} onward)")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_regime_stats(residuals, sigma):
    """Compute regime distribution from residuals"""
    z_scores = residuals / sigma
    
    in_line = (np.abs(z_scores) < 1.0).sum() / len(z_scores)
    stretch = ((np.abs(z_scores) >= 1.0) & (np.abs(z_scores) < 2.0)).sum() / len(z_scores)
    break_regime = (np.abs(z_scores) >= 2.0).sum() / len(z_scores)
    
    return {
        'in_line_pct': in_line,
        'stretch_pct': stretch,
        'break_pct': break_regime,
        'median_abs_z': np.median(np.abs(z_scores)),
        'max_abs_z': np.max(np.abs(z_scores))
    }

def compute_stability_metrics(fair_value_series):
    """Measure FV stability - want smooth, not jumpy"""
    # Monthly changes
    fv_changes = fair_value_series.diff()
    
    # Volatility of FV itself (not a bug - want stable FV)
    fv_volatility = fair_value_series.std()
    
    # Volatility of FV changes (want low)
    change_volatility = fv_changes.std()
    
    # Max single-month jump
    max_jump = fv_changes.abs().max()
    
    return {
        'fv_std': fv_volatility,
        'change_std': change_volatility,
        'max_monthly_jump': max_jump,
        'mean_abs_change': fv_changes.abs().mean()
    }

def get_top_features(model, feature_names, n=15):
    """Extract most important features"""
    if hasattr(model, 'coef_'):
        # Linear models
        coef_abs = np.abs(model.coef_)
        top_idx = np.argsort(coef_abs)[-n:][::-1]
        return [(feature_names[i], model.coef_[i]) for i in top_idx]
    elif hasattr(model, 'feature_importances_'):
        # Tree models
        importances = model.feature_importances_
        top_idx = np.argsort(importances)[-n:][::-1]
        return [(feature_names[i], importances[i]) for i in top_idx]
    else:
        return []

# ============================================================================
# MODEL 1: RIDGE BASELINE
# ============================================================================

print("\n" + "="*80)
print("[MODEL 1/5] RIDGE BASELINE")
print("="*80)

ridge = RidgeCV(alphas=[0.01, 0.1, 1, 10, 100, 500, 1000], cv=5)
ridge.fit(X_train, y_train)

ridge_train_pred = ridge.predict(X_train)
ridge_test_pred = ridge.predict(X_test) if len(X_test) > 0 else np.array([])
ridge_full_pred = ridge.predict(X_full)

# Training residuals for sigma
ridge_train_resid = y_train.values - ridge_train_pred
ridge_sigma = ridge_train_resid.std()

# Test performance
ridge_test_resid = y_test.values - ridge_test_pred if len(X_test) > 0 else np.array([])

ridge_results = {
    'name': 'Ridge Baseline',
    'model': ridge,
    'train_pred': ridge_train_pred,
    'test_pred': ridge_test_pred,
    'full_pred': ridge_full_pred,
    'sigma': ridge_sigma,
    'train_resid': ridge_train_resid,
    'test_resid': ridge_test_resid,
    'metrics': {
        'best_alpha': ridge.alpha_,
        'r2_train': r2_score(y_train, ridge_train_pred),
        'r2_test': r2_score(y_test, ridge_test_pred) if len(X_test) > 0 else np.nan,
        'rmse_train': np.sqrt(mean_squared_error(y_train, ridge_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, ridge_test_pred)) if len(X_test) > 0 else np.nan,
        'regime_stats_train': compute_regime_stats(ridge_train_resid, ridge_sigma),
        'regime_stats_test': compute_regime_stats(ridge_test_resid, ridge_sigma) if len(X_test) > 0 else {},
        'stability': compute_stability_metrics(pd.Series(ridge_full_pred, index=y_full.index))
    }
}

print(f"  Best alpha: {ridge.alpha_:.1f}")
print(f"  R² train: {ridge_results['metrics']['r2_train']:.3f}")
print(f"  R² test:  {ridge_results['metrics']['r2_test']:.3f}" if len(X_test) > 0 else "")
print(f"  RMSE train: {ridge_results['metrics']['rmse_train']:.4f}")
print(f"  RMSE test:  {ridge_results['metrics']['rmse_test']:.4f}" if len(X_test) > 0 else "")
print(f"  Training σ: {ridge_sigma:.5f}")
print(f"\n  Regime frequency (training):")
print(f"    In-line (<1σ):  {ridge_results['metrics']['regime_stats_train']['in_line_pct']:.1%}")
print(f"    Stretch (1-2σ): {ridge_results['metrics']['regime_stats_train']['stretch_pct']:.1%}")
print(f"    Break (>2σ):    {ridge_results['metrics']['regime_stats_train']['break_pct']:.1%}")
print(f"\n  FV Stability:")
print(f"    Mean monthly change: {ridge_results['metrics']['stability']['mean_abs_change']:.5f}")
print(f"    Max monthly jump:    {ridge_results['metrics']['stability']['max_monthly_jump']:.5f}")

top_features = get_top_features(ridge, X_train.columns, 10)
print(f"\n  Top 10 features:")
for feat, coef in top_features:
    print(f"    {feat:40s} {coef:+.6f}")

# ============================================================================
# MODEL 2: LASSO
# ============================================================================

print("\n" + "="*80)
print("[MODEL 2/5] LASSO (L1 Regularization)")
print("="*80)

# Standardize for Lasso
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test) if len(X_test) > 0 else np.array([])
X_full_scaled = scaler.transform(X_full)

lasso = LassoCV(alphas=[0.00001, 0.0001, 0.001, 0.01, 0.1], cv=5, max_iter=10000)
lasso.fit(X_train_scaled, y_train)

lasso_train_pred = lasso.predict(X_train_scaled)
lasso_test_pred = lasso.predict(X_test_scaled) if len(X_test) > 0 else np.array([])
lasso_full_pred = lasso.predict(X_full_scaled)

lasso_train_resid = y_train.values - lasso_train_pred
lasso_sigma = lasso_train_resid.std()
lasso_test_resid = y_test.values - lasso_test_pred if len(X_test) > 0 else np.array([])

n_features_selected = np.sum(np.abs(lasso.coef_) > 1e-5)

lasso_results = {
    'name': 'Lasso',
    'model': lasso,
    'scaler': scaler,
    'train_pred': lasso_train_pred,
    'test_pred': lasso_test_pred,
    'full_pred': lasso_full_pred,
    'sigma': lasso_sigma,
    'train_resid': lasso_train_resid,
    'test_resid': lasso_test_resid,
    'metrics': {
        'best_alpha': lasso.alpha_,
        'n_features_selected': n_features_selected,
        'r2_train': r2_score(y_train, lasso_train_pred),
        'r2_test': r2_score(y_test, lasso_test_pred) if len(X_test) > 0 else np.nan,
        'rmse_train': np.sqrt(mean_squared_error(y_train, lasso_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, lasso_test_pred)) if len(X_test) > 0 else np.nan,
        'regime_stats_train': compute_regime_stats(lasso_train_resid, lasso_sigma),
        'regime_stats_test': compute_regime_stats(lasso_test_resid, lasso_sigma) if len(X_test) > 0 else {},
        'stability': compute_stability_metrics(pd.Series(lasso_full_pred, index=y_full.index))
    }
}

print(f"  Best alpha: {lasso.alpha_:.5f}")
print(f"  Features selected: {n_features_selected}/{len(X_train.columns)}")
print(f"  R² train: {lasso_results['metrics']['r2_train']:.3f}")
print(f"  R² test:  {lasso_results['metrics']['r2_test']:.3f}" if len(X_test) > 0 else "")
print(f"  RMSE train: {lasso_results['metrics']['rmse_train']:.4f}")
print(f"  RMSE test:  {lasso_results['metrics']['rmse_test']:.4f}" if len(X_test) > 0 else "")
print(f"\n  Regime frequency (training):")
print(f"    In-line (<1σ):  {lasso_results['metrics']['regime_stats_train']['in_line_pct']:.1%}")
print(f"    Stretch (1-2σ): {lasso_results['metrics']['regime_stats_train']['stretch_pct']:.1%}")
print(f"    Break (>2σ):    {lasso_results['metrics']['regime_stats_train']['break_pct']:.1%}")

top_features = get_top_features(lasso, X_train.columns, 10)
print(f"\n  Top 10 features (selected):")
for feat, coef in top_features:
    if abs(coef) > 1e-5:
        print(f"    {feat:40s} {coef:+.6f}")

# ============================================================================
# MODEL 3: ELASTIC NET
# ============================================================================

print("\n" + "="*80)
print("[MODEL 3/5] ELASTIC NET (L1 + L2)")
print("="*80)

enet = ElasticNetCV(
    alphas=[0.00001, 0.0001, 0.001, 0.01, 0.1],
    l1_ratio=[.1, .3, .5, .7, .9, .95, .99],
    cv=5,
    max_iter=10000
)
enet.fit(X_train_scaled, y_train)

enet_train_pred = enet.predict(X_train_scaled)
enet_test_pred = enet.predict(X_test_scaled) if len(X_test) > 0 else np.array([])
enet_full_pred = enet.predict(X_full_scaled)

enet_train_resid = y_train.values - enet_train_pred
enet_sigma = enet_train_resid.std()
enet_test_resid = y_test.values - enet_test_pred if len(X_test) > 0 else np.array([])

n_features_enet = np.sum(np.abs(enet.coef_) > 1e-5)

enet_results = {
    'name': 'ElasticNet',
    'model': enet,
    'scaler': scaler,
    'train_pred': enet_train_pred,
    'test_pred': enet_test_pred,
    'full_pred': enet_full_pred,
    'sigma': enet_sigma,
    'train_resid': enet_train_resid,
    'test_resid': enet_test_resid,
    'metrics': {
        'best_alpha': enet.alpha_,
        'best_l1_ratio': enet.l1_ratio_,
        'n_features_selected': n_features_enet,
        'r2_train': r2_score(y_train, enet_train_pred),
        'r2_test': r2_score(y_test, enet_test_pred) if len(X_test) > 0 else np.nan,
        'rmse_train': np.sqrt(mean_squared_error(y_train, enet_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, enet_test_pred)) if len(X_test) > 0 else np.nan,
        'regime_stats_train': compute_regime_stats(enet_train_resid, enet_sigma),
        'regime_stats_test': compute_regime_stats(enet_test_resid, enet_sigma) if len(X_test) > 0 else {},
        'stability': compute_stability_metrics(pd.Series(enet_full_pred, index=y_full.index))
    }
}

print(f"  Best alpha: {enet.alpha_:.5f}, L1 ratio: {enet.l1_ratio_:.2f}")
print(f"  Features selected: {n_features_enet}/{len(X_train.columns)}")
print(f"  R² train: {enet_results['metrics']['r2_train']:.3f}")
print(f"  R² test:  {enet_results['metrics']['r2_test']:.3f}" if len(X_test) > 0 else "")
print(f"  RMSE train: {enet_results['metrics']['rmse_train']:.4f}")
print(f"  RMSE test:  {enet_results['metrics']['rmse_test']:.4f}" if len(X_test) > 0 else "")
print(f"\n  Regime frequency (training):")
print(f"    In-line (<1σ):  {enet_results['metrics']['regime_stats_train']['in_line_pct']:.1%}")
print(f"    Stretch (1-2σ): {enet_results['metrics']['regime_stats_train']['stretch_pct']:.1%}")
print(f"    Break (>2σ):    {enet_results['metrics']['regime_stats_train']['break_pct']:.1%}")

# ============================================================================
# MODEL 4: XGBOOST SINGLE-STAGE
# ============================================================================

print("\n" + "="*80)
print("[MODEL 4/5] XGBOOST (Single-Stage, Regularized)")
print("="*80)

# Use moderate regularization to prevent overfitting
xgb_single = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=10.0,  # Stronger L2
    reg_alpha=5.0,    # Add L1
    objective="reg:squarederror",
    tree_method="hist",
    random_state=42
)

xgb_single.fit(X_train, y_train, verbose=False)

xgb_single_train_pred = xgb_single.predict(X_train)
xgb_single_test_pred = xgb_single.predict(X_test) if len(X_test) > 0 else np.array([])
xgb_single_full_pred = xgb_single.predict(X_full)

xgb_single_train_resid = y_train.values - xgb_single_train_pred
xgb_single_sigma = xgb_single_train_resid.std()
xgb_single_test_resid = y_test.values - xgb_single_test_pred if len(X_test) > 0 else np.array([])

xgb_single_results = {
    'name': 'XGBoost Single-Stage',
    'model': xgb_single,
    'train_pred': xgb_single_train_pred,
    'test_pred': xgb_single_test_pred,
    'full_pred': xgb_single_full_pred,
    'sigma': xgb_single_sigma,
    'train_resid': xgb_single_train_resid,
    'test_resid': xgb_single_test_resid,
    'metrics': {
        'r2_train': r2_score(y_train, xgb_single_train_pred),
        'r2_test': r2_score(y_test, xgb_single_test_pred) if len(X_test) > 0 else np.nan,
        'rmse_train': np.sqrt(mean_squared_error(y_train, xgb_single_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, xgb_single_test_pred)) if len(X_test) > 0 else np.nan,
        'regime_stats_train': compute_regime_stats(xgb_single_train_resid, xgb_single_sigma),
        'regime_stats_test': compute_regime_stats(xgb_single_test_resid, xgb_single_sigma) if len(X_test) > 0 else {},
        'stability': compute_stability_metrics(pd.Series(xgb_single_full_pred, index=y_full.index))
    }
}

print(f"  R² train: {xgb_single_results['metrics']['r2_train']:.3f}")
print(f"  R² test:  {xgb_single_results['metrics']['r2_test']:.3f}" if len(X_test) > 0 else "")
print(f"  RMSE train: {xgb_single_results['metrics']['rmse_train']:.4f}")
print(f"  RMSE test:  {xgb_single_results['metrics']['rmse_test']:.4f}" if len(X_test) > 0 else "")
print(f"\n  Regime frequency (training):")
print(f"    In-line (<1σ):  {xgb_single_results['metrics']['regime_stats_train']['in_line_pct']:.1%}")
print(f"    Stretch (1-2σ): {xgb_single_results['metrics']['regime_stats_train']['stretch_pct']:.1%}")
print(f"    Break (>2σ):    {xgb_single_results['metrics']['regime_stats_train']['break_pct']:.1%}")

top_features = get_top_features(xgb_single, X_train.columns, 10)
print(f"\n  Top 10 features by importance:")
for feat, imp in top_features:
    print(f"    {feat:40s} {imp:.4f}")

# ============================================================================
# MODEL 5: TWO-STAGE XGBOOST (M1 + M2)
# ============================================================================

print("\n" + "="*80)
print("[MODEL 5/5] TWO-STAGE XGBOOST (M1 + Residual M2)")
print("="*80)

# Use Ridge as M1 (more stable than XGB as base)
print("  Stage 1: Using Ridge as base model (M1)")
m1_train_pred = ridge_train_pred
m1_test_pred = ridge_test_pred
m1_full_pred = ridge_full_pred

# Compute M1 residuals
m1_train_resid = y_train.values - m1_train_pred
m1_sigma = m1_train_resid.std()
m1_test_resid = y_test.values - m1_test_pred if len(X_test) > 0 else np.array([])

print(f"  M1 (Ridge) σ: {m1_sigma:.5f}")

# Augment features with regime indicators
print("\n  Stage 2: Training residual model (M2) with regime awareness")
m1_z_train = m1_train_resid / m1_sigma
m1_z_test = m1_test_resid / m1_sigma if len(X_test) > 0 else np.array([])

# Create augmented features
X_train_aug = X_train.copy()
X_train_aug['m1_residual_z'] = m1_z_train
X_train_aug['regime_break'] = (np.abs(m1_z_train) > 2.0).astype(int)
X_train_aug['regime_stretch'] = ((np.abs(m1_z_train) > 1.0) & (np.abs(m1_z_train) <= 2.0)).astype(int)

if len(X_test) > 0:
    X_test_aug = X_test.copy()
    X_test_aug['m1_residual_z'] = m1_z_test
    X_test_aug['regime_break'] = (np.abs(m1_z_test) > 2.0).astype(int)
    X_test_aug['regime_stretch'] = ((np.abs(m1_z_test) > 1.0) & (np.abs(m1_z_test) <= 2.0)).astype(int)

# Full dataset augmentation for final predictions
m1_full_resid = y_full.values - m1_full_pred
m1_z_full = m1_full_resid / m1_sigma
X_full_aug = X_full.copy()
X_full_aug['m1_residual_z'] = m1_z_full
X_full_aug['regime_break'] = (np.abs(m1_z_full) > 2.0).astype(int)
X_full_aug['regime_stretch'] = ((np.abs(m1_z_full) > 1.0) & (np.abs(m1_z_full) <= 2.0)).astype(int)

# Train M2 on residuals
xgb_m2 = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=2,  # Shallow for residual correction
    subsample=0.7,
    colsample_bytree=0.7,
    reg_lambda=20.0,  # Strong regularization
    reg_alpha=10.0,
    objective="reg:squarederror",
    tree_method="hist",
    random_state=42
)

xgb_m2.fit(X_train_aug, m1_train_resid, verbose=False)

m2_train_pred = xgb_m2.predict(X_train_aug)
m2_test_pred = xgb_m2.predict(X_test_aug) if len(X_test) > 0 else np.array([])
m2_full_pred = xgb_m2.predict(X_full_aug)

# Final predictions = M1 + M2
twostage_train_pred = m1_train_pred + m2_train_pred
twostage_test_pred = m1_test_pred + m2_test_pred if len(X_test) > 0 else np.array([])
twostage_full_pred = m1_full_pred + m2_full_pred

twostage_train_resid = y_train.values - twostage_train_pred
twostage_sigma = twostage_train_resid.std()
twostage_test_resid = y_test.values - twostage_test_pred if len(X_test) > 0 else np.array([])

twostage_results = {
    'name': 'Two-Stage (Ridge + XGB Residual)',
    'model_m1': ridge,
    'model_m2': xgb_m2,
    'train_pred': twostage_train_pred,
    'test_pred': twostage_test_pred,
    'full_pred': twostage_full_pred,
    'sigma': twostage_sigma,
    'train_resid': twostage_train_resid,
    'test_resid': twostage_test_resid,
    'metrics': {
        'r2_train': r2_score(y_train, twostage_train_pred),
        'r2_test': r2_score(y_test, twostage_test_pred) if len(X_test) > 0 else np.nan,
        'rmse_train': np.sqrt(mean_squared_error(y_train, twostage_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, twostage_test_pred)) if len(X_test) > 0 else np.nan,
        'regime_stats_train': compute_regime_stats(twostage_train_resid, twostage_sigma),
        'regime_stats_test': compute_regime_stats(twostage_test_resid, twostage_sigma) if len(X_test) > 0 else {},
        'stability': compute_stability_metrics(pd.Series(twostage_full_pred, index=y_full.index))
    }
}

print(f"  R² train: {twostage_results['metrics']['r2_train']:.3f}")
print(f"  R² test:  {twostage_results['metrics']['r2_test']:.3f}" if len(X_test) > 0 else "")
print(f"  RMSE train: {twostage_results['metrics']['rmse_train']:.4f}")
print(f"  RMSE test:  {twostage_results['metrics']['rmse_test']:.4f}" if len(X_test) > 0 else "")
print(f"\n  Regime frequency (training):")
print(f"    In-line (<1σ):  {twostage_results['metrics']['regime_stats_train']['in_line_pct']:.1%}")
print(f"    Stretch (1-2σ): {twostage_results['metrics']['regime_stats_train']['stretch_pct']:.1%}")
print(f"    Break (>2σ):    {twostage_results['metrics']['regime_stats_train']['break_pct']:.1%}")

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

all_models = {
    'ridge': ridge_results,
    'lasso': lasso_results,
    'elasticnet': enet_results,
    'xgboost_single': xgb_single_results,
    'twostage': twostage_results
}

# Save models
output_dir = Path('fx_layer1_outputs')
output_dir.mkdir(exist_ok=True)

with open(output_dir / 'all_models.pkl', 'wb') as f:
    pickle.dump(all_models, f)
print(f"✓ Saved models: {output_dir / 'all_models.pkl'}")

# Create evaluation JSON
eval_summary = {}
for key, results in all_models.items():
    eval_summary[key] = {
        'name': results['name'],
        'r2_test': float(results['metrics']['r2_test']) if not np.isnan(results['metrics']['r2_test']) else None,
        'rmse_test': float(results['metrics']['rmse_test']) if not np.isnan(results['metrics']['rmse_test']) else None,
        'sigma': float(results['sigma']),
        'regime_train': {
            'in_line_pct': float(results['metrics']['regime_stats_train']['in_line_pct']),
            'stretch_pct': float(results['metrics']['regime_stats_train']['stretch_pct']),
            'break_pct': float(results['metrics']['regime_stats_train']['break_pct'])
        },
        'stability': {
            'mean_abs_change': float(results['metrics']['stability']['mean_abs_change']),
            'max_monthly_jump': float(results['metrics']['stability']['max_monthly_jump']),
            'change_std': float(results['metrics']['stability']['change_std'])
        }
    }

with open(output_dir / 'evaluation_summary.json', 'w') as f:
    json.dump(eval_summary, f, indent=2)
print(f"✓ Saved evaluation: {output_dir / 'evaluation_summary.json'}")

# Save predictions CSV for each model
for key, results in all_models.items():
    pred_df = pd.DataFrame({
        'date': y_full.index,
        'spot': y_full.values,
        'fair_value': results['full_pred'],
        'mispricing': y_full.values - results['full_pred'],
        'mispricing_z': (y_full.values - results['full_pred']) / results['sigma']
    })
    
    # Add regime labels
    def get_regime(z):
        abs_z = abs(z)
        if abs_z < 1.0:
            return "In-line"
        elif abs_z < 2.0:
            return "Stretch"
        else:
            return "Break"
    
    pred_df['regime'] = pred_df['mispricing_z'].apply(get_regime)
    
    # Add bands
    pred_df['fv_plus_1sigma'] = pred_df['fair_value'] + results['sigma']
    pred_df['fv_minus_1sigma'] = pred_df['fair_value'] - results['sigma']
    pred_df['fv_plus_2sigma'] = pred_df['fair_value'] + 2 * results['sigma']
    pred_df['fv_minus_2sigma'] = pred_df['fair_value'] - 2 * results['sigma']
    
    pred_df.to_csv(output_dir / f'{key}_predictions.csv', index=False)
    print(f"✓ Saved predictions: {output_dir / f'{key}_predictions.csv'}")

print("\n" + "="*80)
print("✅ LAYER 1 TRAINING COMPLETE")
print("="*80)
print(f"\nNext step: Run evaluation dashboard to compare models")
print(f"  python fx_layer1_evaluation_dashboard.py")


