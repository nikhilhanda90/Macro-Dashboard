"""
FX Layer 2: LightGBM-Only Training
Standalone script to train LightGBM models without sklearn dependencies
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path

print("="*80)
print("FX LAYER 2 - LIGHTGBM STANDALONE TRAINING")
print("="*80)

# Import LightGBM
try:
    from lightgbm import LGBMRegressor, LGBMClassifier
    print("[OK] LightGBM imported successfully")
except ModuleNotFoundError:
    print("[ERROR] LightGBM not installed")
    exit(1)

# Load weekly features and prepare data
print("\n[1] Preparing training data...")

# Load Layer 1 recommendation to get sigma
with open('fx_layer1_outputs/layer1_recommendation.json', 'r') as f:
    layer1_rec = json.load(f)
sigma = layer1_rec['sigma']
model_key = layer1_rec['model_key']

# Load Layer 1 monthly data
layer1_data = pd.read_pickle('fx_layer1_outputs/all_models.pkl')
monthly_full = layer1_data[model_key]['monthly_full']

# Load weekly features
weekly_features = pd.read_pickle('fx_layer2_outputs/weekly_features.pkl')

# Merge with monthly FV
weekly_with_fv = weekly_features.merge(
    monthly_full[['date', 'spot', 'fair_value', 'mispricing', 'z_score']],
    on='date',
    how='left'
).ffill()

# Create targets
weekly_with_fv['delta_z'] = weekly_with_fv['z_score'].diff()
weekly_with_fv['expanding'] = (weekly_with_fv['delta_z'] > 0).astype(int)

# Drop first row (NaN delta)
weekly_with_fv = weekly_with_fv.iloc[1:].reset_index(drop=True)

# Train/test split (2025 = test)
split_date = '2025-01-01'
train_mask = weekly_with_fv['date'] < split_date
test_mask = weekly_with_fv['date'] >= split_date

# Features (exclude date and target columns)
feature_cols = [c for c in weekly_with_fv.columns 
                if c not in ['date', 'spot', 'fair_value', 'mispricing', 'z_score', 'delta_z', 'expanding']]

X_train = weekly_with_fv.loc[train_mask, feature_cols].values
X_test = weekly_with_fv.loc[test_mask, feature_cols].values
y_train_delta_z = weekly_with_fv.loc[train_mask, 'delta_z'].values
y_test_delta_z = weekly_with_fv.loc[test_mask, 'delta_z'].values
y_train_binary = weekly_with_fv.loc[train_mask, 'expanding'].values
y_test_binary = weekly_with_fv.loc[test_mask, 'expanding'].values
test_z = weekly_with_fv.loc[test_mask, 'z_score'].values

print(f"  [OK] Training data: {len(X_train)} samples, {X_train.shape[1]} features")
print(f"  [OK] Test data: {len(X_test)} samples")

# Scale data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Load existing models to merge with
with open('fx_layer2_outputs/all_models.pkl', 'rb') as f:
    existing = pickle.load(f)

print("\n" + "="*80)
print("TARGET A: Δz (Change in Mispricing Z-Score)")
print("="*80)

print("\n[MODEL A4] LightGBM Regressor...")
lgbm_delta_z = LGBMRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    num_leaves=7,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=5.0,
    reg_alpha=2.0,
    random_state=42,
    verbosity=-1
)

lgbm_delta_z.fit(X_train_scaled, y_train_delta_z)

# Predictions
pred_train_delta_z = lgbm_delta_z.predict(X_train_scaled)
pred_test_delta_z = lgbm_delta_z.predict(X_test_scaled)

# Calculate hit rates
def hit_rate(y_true, y_pred):
    """Hit rate: % of correct directional predictions"""
    return np.mean((y_true * y_pred) > 0)

hr_train = hit_rate(y_train_delta_z, pred_train_delta_z)
hr_test = hit_rate(y_test_delta_z, pred_test_delta_z)

# RMSE
rmse_train = np.sqrt(np.mean((y_train_delta_z - pred_train_delta_z)**2))
rmse_test = np.sqrt(np.mean((y_test_delta_z - pred_test_delta_z)**2))

print(f"  Hit rate train: {hr_train:.1%}")
print(f"  Hit rate test:  {hr_test:.1%}")
print(f"  RMSE train: {rmse_train:.4f}")
print(f"  RMSE test:  {rmse_test:.4f}")

# Hit rate when |z| > 1σ
high_z_mask = np.abs(test_z) > 1.0
if high_z_mask.sum() > 0:
    hr_high_z = hit_rate(y_test_delta_z[high_z_mask], pred_test_delta_z[high_z_mask])
    print(f"  Hit rate (|z|>1σ): {hr_high_z:.1%}")
else:
    hr_high_z = None
    print(f"  Hit rate (|z|>1σ): N/A (no high-z test samples)")

print("\n" + "="*80)
print("TARGET B: Binary (Expanding vs Compressing)")
print("="*80)

print("\n[MODEL B4] LightGBM Classifier...")
lgbm_binary = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    num_leaves=7,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=5.0,
    reg_alpha=2.0,
    random_state=42,
    verbosity=-1
)

lgbm_binary.fit(X_train_scaled, y_train_binary)

# Predictions
pred_train_binary = lgbm_binary.predict(X_train_scaled)
pred_test_binary = lgbm_binary.predict(X_test_scaled)

# Accuracy
acc_train = np.mean(y_train_binary == pred_train_binary)
acc_test = np.mean(y_test_binary == pred_test_binary)

print(f"  Accuracy train: {acc_train:.1%}")
print(f"  Accuracy test:  {acc_test:.1%}")

# Accuracy when |z| > 1σ
if high_z_mask.sum() > 0:
    acc_high_z = np.mean(y_test_binary[high_z_mask] == pred_test_binary[high_z_mask])
    print(f"  Accuracy (|z|>1σ): {acc_high_z:.1%}")
else:
    acc_high_z = None
    print(f"  Accuracy (|z|>1σ): N/A")

# Save LightGBM models
print("\n" + "="*80)
print("SAVING LIGHTGBM MODELS")
print("="*80)

# Add LightGBM to existing models
existing['delta_z']['lightgbm'] = {
    'model': lgbm_delta_z,
    'predictions': {
        'train': pred_train_delta_z,
        'test': pred_test_delta_z
    },
    'metrics': {
        'hit_rate_train': hr_train,
        'hit_rate_test': hr_test,
        'hit_rate_high_z': hr_high_z,
        'rmse_train': rmse_train,
        'rmse_test': rmse_test
    }
}

existing['binary']['lightgbm'] = {
    'model': lgbm_binary,
    'predictions': {
        'train': pred_train_binary,
        'test': pred_test_binary
    },
    'metrics': {
        'accuracy_train': acc_train,
        'accuracy_test': acc_test,
        'accuracy_high_z': acc_high_z
    }
}

# Save updated models
with open('fx_layer2_outputs/all_models.pkl', 'wb') as f:
    pickle.dump(existing, f)

print("[OK] Saved to fx_layer2_outputs/all_models.pkl")

# Update evaluation summary
eval_summary = {
    'delta_z': {
        'ridge': {
            'name': 'Ridge',
            'hit_rate_test': existing['delta_z']['ridge']['metrics']['hit_rate_test'],
            'hit_rate_high_z': existing['delta_z']['ridge']['metrics']['hit_rate_high_z'],
            'rmse_test': existing['delta_z']['ridge']['metrics']['rmse_test']
        },
        'elasticnet': {
            'name': 'ElasticNet',
            'hit_rate_test': existing['delta_z']['elasticnet']['metrics']['hit_rate_test'],
            'hit_rate_high_z': existing['delta_z']['elasticnet']['metrics']['hit_rate_high_z'],
            'rmse_test': existing['delta_z']['elasticnet']['metrics']['rmse_test']
        },
        'xgboost': {
            'name': 'XGBoost',
            'hit_rate_test': existing['delta_z']['xgboost']['metrics']['hit_rate_test'],
            'hit_rate_high_z': existing['delta_z']['xgboost']['metrics']['hit_rate_high_z'],
            'rmse_test': existing['delta_z']['xgboost']['metrics']['rmse_test']
        },
        'lightgbm': {
            'name': 'LightGBM',
            'hit_rate_test': hr_test,
            'hit_rate_high_z': hr_high_z,
            'rmse_test': rmse_test
        }
    },
    'binary': {
        'ridge': {
            'name': 'Ridge',
            'accuracy_test': existing['binary']['ridge']['metrics']['accuracy_test'],
            'accuracy_high_z': existing['binary']['ridge']['metrics']['accuracy_high_z']
        },
        'elasticnet': {
            'name': 'ElasticNet',
            'accuracy_test': existing['binary']['elasticnet']['metrics']['accuracy_test'],
            'accuracy_high_z': existing['binary']['elasticnet']['metrics']['accuracy_high_z']
        },
        'xgboost': {
            'name': 'XGBoost',
            'accuracy_test': existing['binary']['xgboost']['metrics']['accuracy_test'],
            'accuracy_high_z': existing['binary']['xgboost']['metrics']['accuracy_high_z']
        },
        'lightgbm': {
            'name': 'LightGBM',
            'accuracy_test': acc_test,
            'accuracy_high_z': acc_high_z
        }
    }
}

with open('fx_layer2_outputs/evaluation_summary.json', 'w') as f:
    json.dump(eval_summary, f, indent=2)

print("[OK] Updated fx_layer2_outputs/evaluation_summary.json")

print("\n" + "="*80)
print("LIGHTGBM SUMMARY")
print("="*80)
print(f"\nDelta-z Target:")
print(f"  Hit Rate: {hr_test:.1%}")
print(f"  Hit Rate (|z|>1sigma): {hr_high_z:.1%}" if hr_high_z else "  Hit Rate (|z|>1sigma): N/A")
print(f"  RMSE: {rmse_test:.4f}")

print(f"\nBinary Target:")
print(f"  Accuracy: {acc_test:.1%}")
print(f"  Accuracy (|z|>1sigma): {acc_high_z:.1%}" if acc_high_z else "  Accuracy (|z|>1sigma): N/A")

print("\n[SUCCESS] LightGBM training complete!")
print("="*80)

