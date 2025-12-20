"""
FX LAYER 2 - WEEKLY PRESSURE SIGNAL MODELS
Train models to predict weekly changes in mispricing

TARGET OPTIONS:
  Option A: Δz (change in mispricing z-score)
  Option B: Binary (expanding=1 vs compressing=0)

MODELS TO TEST:
  - Ridge
  - ElasticNet
  - XGBoost
  - LightGBM

EVALUATION:
  - Hit rate (directional accuracy)
  - Performance when |mispricing| > 1σ
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.linear_model import RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score
from xgboost import XGBRegressor, XGBClassifier
import json

# Try to import LightGBM (optional)
try:
    from lightgbm import LGBMRegressor, LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️  LightGBM not available - will skip LightGBM models")

print("="*80)
print("FX LAYER 2 - WEEKLY PRESSURE SIGNAL MODELS")
print("="*80)
print("Purpose: Predict weekly pressure on FX mispricing")
print("="*80)

# ============================================================================
# 1. LOAD LAYER 1 FAIR VALUE
# ============================================================================

print("\n[1] Loading Layer 1 fair value (monthly)...")

# Load Layer 1 recommendation to get best model
layer1_dir = Path('fx_layer1_outputs')
with open(layer1_dir / 'layer1_recommendation.json', 'r') as f:
    layer1_rec = json.load(f)

best_model_key = layer1_rec['selected_model']
print(f"  ✓ Layer 1 model: {layer1_rec['model_name']}")

# Load Layer 1 predictions (monthly)
layer1_pred = pd.read_csv(layer1_dir / f'{best_model_key}_predictions.csv', parse_dates=['date'])
layer1_pred = layer1_pred.set_index('date')
print(f"  ✓ Loaded monthly fair value: {len(layer1_pred)} months")

# ============================================================================
# 2. LOAD WEEKLY FEATURES
# ============================================================================

print("\n[2] Loading weekly features...")

with open('fx_layer2_weekly_features.pkl', 'rb') as f:
    weekly_features = pickle.load(f)

print(f"  ✓ Loaded weekly features: {len(weekly_features)} weeks, {len(weekly_features.columns)-1} features")

# ============================================================================
# 3. MAP MONTHLY FV TO WEEKLY FREQUENCY
# ============================================================================

print("\n[3] Mapping monthly fair value to weekly frequency...")

# For each week, use the fair value from the most recent month
weekly_fv = pd.DataFrame(index=weekly_features.index)
weekly_fv['spot'] = weekly_features['spot']

# Forward-fill monthly FV to weekly
layer1_monthly = layer1_pred[['fair_value', 'mispricing_z']].copy()
layer1_monthly.index = pd.to_datetime(layer1_monthly.index)

# Reindex to weekly and forward-fill
weekly_fv['fair_value'] = layer1_monthly['fair_value'].reindex(
    weekly_fv.index, method='ffill'
)
weekly_fv['mispricing'] = weekly_fv['spot'] - weekly_fv['fair_value']

# Compute z-score using Layer 1 sigma
layer1_sigma = layer1_rec['metrics']['sigma']
weekly_fv['mispricing_z'] = weekly_fv['mispricing'] / layer1_sigma

print(f"  ✓ Mapped to weekly frequency using Layer 1 σ = {layer1_sigma:.5f}")
print(f"  ✓ Current mispricing: {weekly_fv['mispricing_z'].iloc[-1]:.2f}σ")

# ============================================================================
# 4. CREATE TARGET VARIABLES
# ============================================================================

print("\n[4] Creating target variables...")

# TARGET A: Δz (change in mispricing z-score)
weekly_fv['target_delta_z'] = weekly_fv['mispricing_z'].diff(1)

# TARGET B: Binary (expanding=1, compressing=0)
# Expanding = |mispricing| is getting larger
# Compressing = |mispricing| is getting smaller
abs_mispricing_change = weekly_fv['mispricing_z'].abs().diff(1)
weekly_fv['target_binary'] = (abs_mispricing_change > 0).astype(int)

print(f"  ✓ Target A (Δz): mean={weekly_fv['target_delta_z'].mean():.4f}, std={weekly_fv['target_delta_z'].std():.4f}")
print(f"  ✓ Target B (Binary): expanding={weekly_fv['target_binary'].mean():.1%}, compressing={1-weekly_fv['target_binary'].mean():.1%}")

# ============================================================================
# 5. MERGE WITH FEATURES
# ============================================================================

print("\n[5] Merging with weekly features...")

# Merge
df_full = weekly_features.drop('spot', axis=1).join(weekly_fv, how='inner')
df_full = df_full.dropna()

print(f"  ✓ Merged dataset: {len(df_full)} weeks")
print(f"  ✓ Date range: {df_full.index.min().strftime('%Y-%m-%d')} to {df_full.index.max().strftime('%Y-%m-%d')}")

# ============================================================================
# 6. TRAIN/TEST SPLIT
# ============================================================================

print("\n[6] Train/Test split...")

TRAIN_END = '2024-12-31'
train_df = df_full[df_full.index <= TRAIN_END]
test_df = df_full[df_full.index > TRAIN_END]

# Feature columns (exclude targets and mispricing columns)
feature_cols = [c for c in df_full.columns if c not in [
    'spot', 'fair_value', 'mispricing', 'mispricing_z',
    'target_delta_z', 'target_binary'
]]

X_train = train_df[feature_cols]
X_test = test_df[feature_cols]

y_train_delta_z = train_df['target_delta_z']
y_test_delta_z = test_df['target_delta_z']

y_train_binary = train_df['target_binary']
y_test_binary = test_df['target_binary']

# Mispricing z-scores for conditional evaluation
z_train = train_df['mispricing_z']
z_test = test_df['mispricing_z']

print(f"  Train: {len(X_train)} weeks (to {TRAIN_END})")
print(f"  Test:  {len(X_test)} weeks ({test_df.index.min().strftime('%Y-%m-%d')} onward)")
print(f"  Features: {len(feature_cols)}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def directional_accuracy(y_true, y_pred):
    """Hit rate: % of correct directional predictions"""
    return np.mean(np.sign(y_true) == np.sign(y_pred))

def conditional_accuracy(y_true, y_pred, condition_mask):
    """Accuracy conditional on some condition"""
    if condition_mask.sum() == 0:
        return np.nan
    return np.mean(np.sign(y_true[condition_mask]) == np.sign(y_pred[condition_mask]))

# ============================================================================
# TARGET A: Δz (REGRESSION MODELS)
# ============================================================================

print("\n" + "="*80)
print("TARGET A: Δz (Change in Mispricing Z-Score)")
print("="*80)

results_delta_z = {}

# -------------------------------------------------------------------------------
# A1: Ridge
# -------------------------------------------------------------------------------
print("\n[MODEL A1] Ridge Regression...")

ridge_delta_z = RidgeCV(alphas=[0.1, 1, 10, 100, 500], cv=5)
ridge_delta_z.fit(X_train, y_train_delta_z)

ridge_train_pred = ridge_delta_z.predict(X_train)
ridge_test_pred = ridge_delta_z.predict(X_test) if len(X_test) > 0 else np.array([])

ridge_hit_train = directional_accuracy(y_train_delta_z.values, ridge_train_pred)
ridge_hit_test = directional_accuracy(y_test_delta_z.values, ridge_test_pred) if len(X_test) > 0 else np.nan

# Conditional accuracy when |z| > 1σ
high_z_test = np.abs(z_test.values) > 1.0
ridge_hit_high_z = conditional_accuracy(y_test_delta_z.values, ridge_test_pred, high_z_test) if len(X_test) > 0 else np.nan

results_delta_z['ridge'] = {
    'name': 'Ridge',
    'model': ridge_delta_z,
    'hit_rate_train': ridge_hit_train,
    'hit_rate_test': ridge_hit_test,
    'hit_rate_high_z': ridge_hit_high_z,
    'rmse_train': np.sqrt(mean_squared_error(y_train_delta_z, ridge_train_pred)),
    'rmse_test': np.sqrt(mean_squared_error(y_test_delta_z, ridge_test_pred)) if len(X_test) > 0 else np.nan,
    'test_pred': ridge_test_pred
}

print(f"  Hit rate train: {ridge_hit_train:.1%}")
print(f"  Hit rate test:  {ridge_hit_test:.1%}" if len(X_test) > 0 else "")
print(f"  Hit rate (|z|>1σ): {ridge_hit_high_z:.1%}" if len(X_test) > 0 else "")

# -------------------------------------------------------------------------------
# A2: ElasticNet
# -------------------------------------------------------------------------------
print("\n[MODEL A2] ElasticNet...")

scaler_delta_z = StandardScaler()
X_train_scaled = scaler_delta_z.fit_transform(X_train)
X_test_scaled = scaler_delta_z.transform(X_test) if len(X_test) > 0 else np.array([])

enet_delta_z = ElasticNetCV(
    alphas=[0.001, 0.01, 0.1, 1],
    l1_ratio=[.1, .5, .7, .9, .95],
    cv=5,
    max_iter=5000
)
enet_delta_z.fit(X_train_scaled, y_train_delta_z)

enet_train_pred = enet_delta_z.predict(X_train_scaled)
enet_test_pred = enet_delta_z.predict(X_test_scaled) if len(X_test) > 0 else np.array([])

enet_hit_train = directional_accuracy(y_train_delta_z.values, enet_train_pred)
enet_hit_test = directional_accuracy(y_test_delta_z.values, enet_test_pred) if len(X_test) > 0 else np.nan
enet_hit_high_z = conditional_accuracy(y_test_delta_z.values, enet_test_pred, high_z_test) if len(X_test) > 0 else np.nan

results_delta_z['elasticnet'] = {
    'name': 'ElasticNet',
    'model': enet_delta_z,
    'scaler': scaler_delta_z,
    'hit_rate_train': enet_hit_train,
    'hit_rate_test': enet_hit_test,
    'hit_rate_high_z': enet_hit_high_z,
    'rmse_train': np.sqrt(mean_squared_error(y_train_delta_z, enet_train_pred)),
    'rmse_test': np.sqrt(mean_squared_error(y_test_delta_z, enet_test_pred)) if len(X_test) > 0 else np.nan,
    'test_pred': enet_test_pred
}

print(f"  Hit rate train: {enet_hit_train:.1%}")
print(f"  Hit rate test:  {enet_hit_test:.1%}" if len(X_test) > 0 else "")
print(f"  Hit rate (|z|>1σ): {enet_hit_high_z:.1%}" if len(X_test) > 0 else "")

# -------------------------------------------------------------------------------
# A3: XGBoost
# -------------------------------------------------------------------------------
print("\n[MODEL A3] XGBoost...")

xgb_delta_z = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=5.0,
    reg_alpha=2.0,
    random_state=42
)
xgb_delta_z.fit(X_train, y_train_delta_z, verbose=False)

xgb_train_pred = xgb_delta_z.predict(X_train)
xgb_test_pred = xgb_delta_z.predict(X_test) if len(X_test) > 0 else np.array([])

xgb_hit_train = directional_accuracy(y_train_delta_z.values, xgb_train_pred)
xgb_hit_test = directional_accuracy(y_test_delta_z.values, xgb_test_pred) if len(X_test) > 0 else np.nan
xgb_hit_high_z = conditional_accuracy(y_test_delta_z.values, xgb_test_pred, high_z_test) if len(X_test) > 0 else np.nan

results_delta_z['xgboost'] = {
    'name': 'XGBoost',
    'model': xgb_delta_z,
    'hit_rate_train': xgb_hit_train,
    'hit_rate_test': xgb_hit_test,
    'hit_rate_high_z': xgb_hit_high_z,
    'rmse_train': np.sqrt(mean_squared_error(y_train_delta_z, xgb_train_pred)),
    'rmse_test': np.sqrt(mean_squared_error(y_test_delta_z, xgb_test_pred)) if len(X_test) > 0 else np.nan,
    'test_pred': xgb_test_pred
}

print(f"  Hit rate train: {xgb_hit_train:.1%}")
print(f"  Hit rate test:  {xgb_hit_test:.1%}" if len(X_test) > 0 else "")
print(f"  Hit rate (|z|>1σ): {xgb_hit_high_z:.1%}" if len(X_test) > 0 else "")

# -------------------------------------------------------------------------------
# A4: LightGBM
# -------------------------------------------------------------------------------
if LIGHTGBM_AVAILABLE:
    print("\n[MODEL A4] LightGBM...")

    lgbm_delta_z = LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=5.0,
        reg_alpha=2.0,
        random_state=42,
        verbose=-1
    )
    lgbm_delta_z.fit(X_train, y_train_delta_z)

    lgbm_train_pred = lgbm_delta_z.predict(X_train)
    lgbm_test_pred = lgbm_delta_z.predict(X_test) if len(X_test) > 0 else np.array([])

    lgbm_hit_train = directional_accuracy(y_train_delta_z.values, lgbm_train_pred)
    lgbm_hit_test = directional_accuracy(y_test_delta_z.values, lgbm_test_pred) if len(X_test) > 0 else np.nan
    lgbm_hit_high_z = conditional_accuracy(y_test_delta_z.values, lgbm_test_pred, high_z_test) if len(X_test) > 0 else np.nan

    results_delta_z['lightgbm'] = {
        'name': 'LightGBM',
        'model': lgbm_delta_z,
        'hit_rate_train': lgbm_hit_train,
        'hit_rate_test': lgbm_hit_test,
        'hit_rate_high_z': lgbm_hit_high_z,
        'rmse_train': np.sqrt(mean_squared_error(y_train_delta_z, lgbm_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test_delta_z, lgbm_test_pred)) if len(X_test) > 0 else np.nan,
        'test_pred': lgbm_test_pred
    }

    print(f"  Hit rate train: {lgbm_hit_train:.1%}")
    print(f"  Hit rate test:  {lgbm_hit_test:.1%}" if len(X_test) > 0 else "")
    print(f"  Hit rate (|z|>1σ): {lgbm_hit_high_z:.1%}" if len(X_test) > 0 else "")
else:
    print("\n[MODEL A4] LightGBM... SKIPPED (not installed)")

# ============================================================================
# TARGET B: BINARY (EXPANDING/COMPRESSING - CLASSIFICATION)
# ============================================================================

print("\n" + "="*80)
print("TARGET B: BINARY (Expanding=1 vs Compressing=0)")
print("="*80)

results_binary = {}

# -------------------------------------------------------------------------------
# B1: Ridge (Logistic-style using Ridge)
# -------------------------------------------------------------------------------
print("\n[MODEL B1] Ridge (with threshold)...")

# Use Ridge regression with threshold at 0.5
ridge_binary = RidgeCV(alphas=[0.1, 1, 10, 100, 500], cv=5)
ridge_binary.fit(X_train, y_train_binary)

ridge_bin_train_prob = ridge_binary.predict(X_train)
ridge_bin_train_pred = (ridge_bin_train_prob > 0.5).astype(int)
ridge_bin_test_prob = ridge_binary.predict(X_test) if len(X_test) > 0 else np.array([])
ridge_bin_test_pred = (ridge_bin_test_prob > 0.5).astype(int) if len(X_test) > 0 else np.array([])

ridge_acc_train = accuracy_score(y_train_binary, ridge_bin_train_pred)
ridge_acc_test = accuracy_score(y_test_binary, ridge_bin_test_pred) if len(X_test) > 0 else np.nan
ridge_acc_high_z = accuracy_score(y_test_binary[high_z_test], ridge_bin_test_pred[high_z_test]) if (len(X_test) > 0 and high_z_test.sum() > 0) else np.nan

results_binary['ridge'] = {
    'name': 'Ridge',
    'model': ridge_binary,
    'accuracy_train': ridge_acc_train,
    'accuracy_test': ridge_acc_test,
    'accuracy_high_z': ridge_acc_high_z,
    'test_pred': ridge_bin_test_pred
}

print(f"  Accuracy train: {ridge_acc_train:.1%}")
print(f"  Accuracy test:  {ridge_acc_test:.1%}" if len(X_test) > 0 else "")
print(f"  Accuracy (|z|>1σ): {ridge_acc_high_z:.1%}" if (len(X_test) > 0 and high_z_test.sum() > 0) else "")

# -------------------------------------------------------------------------------
# B2: ElasticNet (with threshold)
# -------------------------------------------------------------------------------
print("\n[MODEL B2] ElasticNet (with threshold)...")

enet_binary = ElasticNetCV(
    alphas=[0.001, 0.01, 0.1, 1],
    l1_ratio=[.1, .5, .7, .9, .95],
    cv=5,
    max_iter=5000
)
enet_binary.fit(X_train_scaled, y_train_binary)

enet_bin_train_prob = enet_binary.predict(X_train_scaled)
enet_bin_train_pred = (enet_bin_train_prob > 0.5).astype(int)
enet_bin_test_prob = enet_binary.predict(X_test_scaled) if len(X_test) > 0 else np.array([])
enet_bin_test_pred = (enet_bin_test_prob > 0.5).astype(int) if len(X_test) > 0 else np.array([])

enet_acc_train = accuracy_score(y_train_binary, enet_bin_train_pred)
enet_acc_test = accuracy_score(y_test_binary, enet_bin_test_pred) if len(X_test) > 0 else np.nan
enet_acc_high_z = accuracy_score(y_test_binary[high_z_test], enet_bin_test_pred[high_z_test]) if (len(X_test) > 0 and high_z_test.sum() > 0) else np.nan

results_binary['elasticnet'] = {
    'name': 'ElasticNet',
    'model': enet_binary,
    'scaler': scaler_delta_z,
    'accuracy_train': enet_acc_train,
    'accuracy_test': enet_acc_test,
    'accuracy_high_z': enet_acc_high_z,
    'test_pred': enet_bin_test_pred
}

print(f"  Accuracy train: {enet_acc_train:.1%}")
print(f"  Accuracy test:  {enet_acc_test:.1%}" if len(X_test) > 0 else "")
print(f"  Accuracy (|z|>1σ): {enet_acc_high_z:.1%}" if (len(X_test) > 0 and high_z_test.sum() > 0) else "")

# -------------------------------------------------------------------------------
# B3: XGBoost Classifier
# -------------------------------------------------------------------------------
print("\n[MODEL B3] XGBoost Classifier...")

xgb_binary = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=5.0,
    reg_alpha=2.0,
    random_state=42,
    eval_metric='logloss'
)
xgb_binary.fit(X_train, y_train_binary, verbose=False)

xgb_bin_train_pred = xgb_binary.predict(X_train)
xgb_bin_test_pred = xgb_binary.predict(X_test) if len(X_test) > 0 else np.array([])

xgb_acc_train = accuracy_score(y_train_binary, xgb_bin_train_pred)
xgb_acc_test = accuracy_score(y_test_binary, xgb_bin_test_pred) if len(X_test) > 0 else np.nan
xgb_acc_high_z = accuracy_score(y_test_binary[high_z_test], xgb_bin_test_pred[high_z_test]) if (len(X_test) > 0 and high_z_test.sum() > 0) else np.nan

results_binary['xgboost'] = {
    'name': 'XGBoost',
    'model': xgb_binary,
    'accuracy_train': xgb_acc_train,
    'accuracy_test': xgb_acc_test,
    'accuracy_high_z': xgb_acc_high_z,
    'test_pred': xgb_bin_test_pred
}

print(f"  Accuracy train: {xgb_acc_train:.1%}")
print(f"  Accuracy test:  {xgb_acc_test:.1%}" if len(X_test) > 0 else "")
print(f"  Accuracy (|z|>1σ): {xgb_acc_high_z:.1%}" if (len(X_test) > 0 and high_z_test.sum() > 0) else "")

# -------------------------------------------------------------------------------
# B4: LightGBM Classifier
# -------------------------------------------------------------------------------
if LIGHTGBM_AVAILABLE:
    print("\n[MODEL B4] LightGBM Classifier...")

    lgbm_binary = LGBMClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=5.0,
        reg_alpha=2.0,
        random_state=42,
        verbose=-1
    )
    lgbm_binary.fit(X_train, y_train_binary)

    lgbm_bin_train_pred = lgbm_binary.predict(X_train)
    lgbm_bin_test_pred = lgbm_binary.predict(X_test) if len(X_test) > 0 else np.array([])

    lgbm_acc_train = accuracy_score(y_train_binary, lgbm_bin_train_pred)
    lgbm_acc_test = accuracy_score(y_test_binary, lgbm_bin_test_pred) if len(X_test) > 0 else np.nan
    lgbm_acc_high_z = accuracy_score(y_test_binary[high_z_test], lgbm_bin_test_pred[high_z_test]) if (len(X_test) > 0 and high_z_test.sum() > 0) else np.nan

    results_binary['lightgbm'] = {
        'name': 'LightGBM',
        'model': lgbm_binary,
        'accuracy_train': lgbm_acc_train,
        'accuracy_test': lgbm_acc_test,
        'accuracy_high_z': lgbm_acc_high_z,
        'test_pred': lgbm_bin_test_pred
    }

    print(f"  Accuracy train: {lgbm_acc_train:.1%}")
    print(f"  Accuracy test:  {lgbm_acc_test:.1%}" if len(X_test) > 0 else "")
    print(f"  Accuracy (|z|>1σ): {lgbm_acc_high_z:.1%}" if (len(X_test) > 0 and high_z_test.sum() > 0) else "")
else:
    print("\n[MODEL B4] LightGBM Classifier... SKIPPED (not installed)")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

output_dir = Path('fx_layer2_outputs')
output_dir.mkdir(exist_ok=True)

# Save all models
all_results = {
    'delta_z': results_delta_z,
    'binary': results_binary,
    'test_dates': test_df.index,
    'test_z': z_test.values
}

with open(output_dir / 'all_models.pkl', 'wb') as f:
    pickle.dump(all_results, f)
print(f"✓ Saved models: {output_dir / 'all_models.pkl'}")

# Create evaluation JSON
eval_summary = {
    'delta_z': {},
    'binary': {}
}

for key, res in results_delta_z.items():
    eval_summary['delta_z'][key] = {
        'name': res['name'],
        'hit_rate_test': float(res['hit_rate_test']) if not np.isnan(res['hit_rate_test']) else None,
        'hit_rate_high_z': float(res['hit_rate_high_z']) if not np.isnan(res['hit_rate_high_z']) else None,
        'rmse_test': float(res['rmse_test']) if not np.isnan(res['rmse_test']) else None
    }

for key, res in results_binary.items():
    eval_summary['binary'][key] = {
        'name': res['name'],
        'accuracy_test': float(res['accuracy_test']) if not np.isnan(res['accuracy_test']) else None,
        'accuracy_high_z': float(res['accuracy_high_z']) if not np.isnan(res['accuracy_high_z']) else None
    }

with open(output_dir / 'evaluation_summary.json', 'w') as f:
    json.dump(eval_summary, f, indent=2)
print(f"✓ Saved evaluation: {output_dir / 'evaluation_summary.json'}")

print("\n" + "="*80)
print("✅ LAYER 2 TRAINING COMPLETE")
print("="*80)
print(f"\nNext step: Run evaluation dashboard")
print(f"  python fx_layer2_evaluation_dashboard.py")

