"""
FX LAYER 2 - EVALUATION DASHBOARD
Compare weekly pressure signal models
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("FX LAYER 2 - EVALUATION DASHBOARD")
print("="*80)

# Load results
results_dir = Path('fx_layer2_outputs')
with open(results_dir / 'all_models.pkl', 'rb') as f:
    all_results = pickle.load(f)

with open(results_dir / 'evaluation_summary.json', 'r') as f:
    eval_summary = json.load(f)

results_delta_z = all_results['delta_z']
results_binary = all_results['binary']
test_dates = all_results['test_dates']
test_z = all_results['test_z']

print("\n✓ Loaded results for 8 models (4 per target)")

# ============================================================================
# TARGET A: Δz - COMPARISON TABLE
# ============================================================================

print("\n" + "="*90)
print("TARGET A: Δz (Change in Mispricing Z-Score)")
print("="*90)
print("\nEvaluation Criteria:")
print("  1. Hit rate (test) - directional accuracy")
print("  2. Hit rate when |z| > 1σ - performance when mispricing is stretched")
print("  3. RMSE (magnitude of errors)")
print("\n" + "-"*90)

print(f"\n{'Model':<20} {'Hit Rate Test':>15} {'Hit Rate (|z|>1σ)':>20} {'RMSE Test':>15} {'Score':>10}")
print("-" * 90)

# Get available models only
available_models = [k for k in ['ridge', 'elasticnet', 'xgboost', 'lightgbm'] if k in results_delta_z]

for key in available_models:
    model_name = results_delta_z[key]['name']
    hit_test = results_delta_z[key]['hit_rate_test']
    hit_high_z = results_delta_z[key]['hit_rate_high_z']
    rmse = results_delta_z[key]['rmse_test']
    
    # Calculate score for comparison
    score = (0.6 * hit_test + 0.4 * hit_high_z) if not np.isnan(hit_high_z) else hit_test
    
    print(f"{model_name:<20} {hit_test:>14.1%} {hit_high_z:>19.1%} {rmse:>15.5f} {score:>9.1%}")

print("-" * 90)
print("\nNote: Score = 60% Hit Rate (test) + 40% Hit Rate (|z|>1σ)")
if 'lightgbm' not in results_delta_z:
    print("⚠️  LightGBM models skipped (package not installed)")
print("="*90)

# Find best model for Δz (only from available models)
delta_z_scores = {}
for key in available_models:
    hit_test = results_delta_z[key]['hit_rate_test']
    hit_high_z = results_delta_z[key]['hit_rate_high_z']
    
    # Score: 60% weight on hit_test, 40% on hit_high_z
    score = (0.6 * hit_test + 0.4 * hit_high_z) if not np.isnan(hit_high_z) else hit_test
    delta_z_scores[key] = score

best_delta_z = max(delta_z_scores.keys(), key=lambda k: delta_z_scores[k])

print(f"\n🏆 BEST MODEL (Δz): {results_delta_z[best_delta_z]['name']}")
print(f"   Hit Rate (test): {results_delta_z[best_delta_z]['hit_rate_test']:.1%}")
print(f"   Hit Rate (|z|>1σ): {results_delta_z[best_delta_z]['hit_rate_high_z']:.1%}")

# ============================================================================
# TARGET B: BINARY - COMPARISON TABLE
# ============================================================================

print("\n" + "="*90)
print("TARGET B: BINARY (Expanding vs Compressing)")
print("="*90)
print("\nEvaluation Criteria:")
print("  1. Accuracy (test) - overall classification accuracy")
print("  2. Accuracy when |z| > 1σ - performance when mispricing is stretched")
print("\n" + "-"*90)

print(f"\n{'Model':<20} {'Accuracy Test':>15} {'Accuracy (|z|>1σ)':>20} {'Score':>10}")
print("-" * 90)

# Get available models only
available_binary_models = [k for k in ['ridge', 'elasticnet', 'xgboost', 'lightgbm'] if k in results_binary]

for key in available_binary_models:
    model_name = results_binary[key]['name']
    acc_test = results_binary[key]['accuracy_test']
    acc_high_z = results_binary[key]['accuracy_high_z']
    
    # Calculate score for comparison
    score = (0.6 * acc_test + 0.4 * acc_high_z) if not np.isnan(acc_high_z) else acc_test
    
    print(f"{model_name:<20} {acc_test:>14.1%} {acc_high_z:>19.1%} {score:>9.1%}")

print("-" * 90)
print("\nNote: Score = 60% Accuracy (test) + 40% Accuracy (|z|>1σ)")
if 'lightgbm' not in results_binary:
    print("⚠️  LightGBM models skipped (package not installed)")
print("="*90)

# Find best model for Binary (only from available models)
binary_scores = {}
for key in available_binary_models:
    acc_test = results_binary[key]['accuracy_test']
    acc_high_z = results_binary[key]['accuracy_high_z']
    
    # Score: 60% weight on acc_test, 40% on acc_high_z
    score = (0.6 * acc_test + 0.4 * acc_high_z) if not np.isnan(acc_high_z) else acc_test
    binary_scores[key] = score

best_binary = max(binary_scores.keys(), key=lambda k: binary_scores[k])

print(f"\n🏆 BEST MODEL (Binary): {results_binary[best_binary]['name']}")
print(f"   Accuracy (test): {results_binary[best_binary]['accuracy_test']:.1%}")
print(f"   Accuracy (|z|>1σ): {results_binary[best_binary]['accuracy_high_z']:.1%}")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

print("\n" + "="*80)
print("GENERATING COMPARISON CHARTS")
print("="*80)

# Chart 1: Hit Rate Comparison (Δz models)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Layer 2 (Δz Target) - Model Comparison', 
             fontsize=14, fontweight='bold', color='white')

model_names = [results_delta_z[k]['name'] for k in available_models]
hit_rates_test = [results_delta_z[k]['hit_rate_test'] * 100 for k in available_models]
hit_rates_high_z = [results_delta_z[k]['hit_rate_high_z'] * 100 for k in available_models]

x = np.arange(len(model_names))
width = 0.35

bars1 = ax1.bar(x - width/2, hit_rates_test, width, label='Test (All)', color='cyan', alpha=0.8)
bars2 = ax1.bar(x + width/2, hit_rates_high_z, width, label='Test (|z|>1σ)', color='orange', alpha=0.8)

ax1.axhline(50, color='red', linestyle='--', alpha=0.5, linewidth=1, label='Random (50%)')
ax1.set_ylabel('Hit Rate (%)', fontsize=11, color='white')
ax1.set_title('Directional Accuracy', fontsize=12, fontweight='bold', color='white')
ax1.set_xticks(x)
ax1.set_xticklabels(model_names, rotation=15, ha='right', fontsize=9, color='white')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_facecolor('#0a0a0a')
ax1.tick_params(colors='white')
for spine in ax1.spines.values():
    spine.set_color('white')

# RMSE comparison
rmse_vals = [results_delta_z[k]['rmse_test'] for k in available_models]
ax2.barh(model_names, rmse_vals, color='green', alpha=0.7)
ax2.set_xlabel('RMSE', fontsize=11, color='white')
ax2.set_title('Prediction Error (Lower is Better)', fontsize=12, fontweight='bold', color='white')
ax2.grid(True, alpha=0.3, axis='x')
ax2.set_facecolor('#0a0a0a')
ax2.tick_params(colors='white', labelsize=9)
for spine in ax2.spines.values():
    spine.set_color('white')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig(results_dir / 'layer2_comparison_delta_z.png', dpi=300, facecolor='#0a0a0a')
plt.close()
print(f"✓ Saved: {results_dir / 'layer2_comparison_delta_z.png'}")

# Chart 2: Accuracy Comparison (Binary models)
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Layer 2 (Binary Target) - Model Comparison',
             fontsize=14, fontweight='bold', color='white')

acc_test = [results_binary[k]['accuracy_test'] * 100 for k in available_binary_models]
acc_high_z = [results_binary[k]['accuracy_high_z'] * 100 for k in available_binary_models]

# Use the same model names for consistency
model_names_binary = [results_binary[k]['name'] for k in available_binary_models]

x = np.arange(len(model_names))
width = 0.35

bars1 = ax.bar(x - width/2, acc_test, width, label='Test (All)', color='cyan', alpha=0.8)
bars2 = ax.bar(x + width/2, acc_high_z, width, label='Test (|z|>1σ)', color='orange', alpha=0.8)

ax.axhline(50, color='red', linestyle='--', alpha=0.5, linewidth=1, label='Random (50%)')
ax.set_ylabel('Accuracy (%)', fontsize=11, color='white')
ax.set_title('Classification Accuracy (Expanding vs Compressing)', fontsize=12, fontweight='bold', color='white')
ax.set_xticks(x)
ax.set_xticklabels(model_names_binary, rotation=15, ha='right', fontsize=9, color='white')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
ax.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig(results_dir / 'layer2_comparison_binary.png', dpi=300, facecolor='#0a0a0a')
plt.close()
print(f"✓ Saved: {results_dir / 'layer2_comparison_binary.png'}")

# ============================================================================
# RECOMMENDATION
# ============================================================================

print("\n" + "="*80)
print("LAYER 2 RECOMMENDATION")
print("="*80)

print(f"\n📊 TARGET SELECTION:")
print(f"\n  Option A (Δz): Best model = {results_delta_z[best_delta_z]['name']}")
print(f"    • Hit rate: {results_delta_z[best_delta_z]['hit_rate_test']:.1%}")
print(f"    • Hit rate (|z|>1σ): {results_delta_z[best_delta_z]['hit_rate_high_z']:.1%}")
print(f"    • Pro: Gives magnitude of pressure")
print(f"    • Con: Harder to interpret")

print(f"\n  Option B (Binary): Best model = {results_binary[best_binary]['name']}")
print(f"    • Accuracy: {results_binary[best_binary]['accuracy_test']:.1%}")
print(f"    • Accuracy (|z|>1σ): {results_binary[best_binary]['accuracy_high_z']:.1%}")
print(f"    • Pro: Simple expanding/compressing signal")
print(f"    • Con: Loses magnitude information")

# Auto-select based on performance
if delta_z_scores[best_delta_z] > binary_scores[best_binary]:
    recommended_target = 'delta_z'
    recommended_model = best_delta_z
    recommended_score = results_delta_z[best_delta_z]['hit_rate_test']
else:
    recommended_target = 'binary'
    recommended_model = best_binary
    recommended_score = results_binary[best_binary]['accuracy_test']

print(f"\n🏆 RECOMMENDED CONFIGURATION:")
print(f"   Target: {recommended_target.upper()}")
print(f"   Model:  {results_delta_z[recommended_model]['name'] if recommended_target == 'delta_z' else results_binary[recommended_model]['name']}")
print(f"   Score:  {recommended_score:.1%}")

# Save recommendation
recommendation = {
    'target': recommended_target,
    'model_key': recommended_model,
    'model_name': results_delta_z[recommended_model]['name'] if recommended_target == 'delta_z' else results_binary[recommended_model]['name'],
    'score': float(recommended_score),
    'metrics': {
        'delta_z_best': {
            'model': results_delta_z[best_delta_z]['name'],
            'hit_rate_test': float(results_delta_z[best_delta_z]['hit_rate_test']),
            'hit_rate_high_z': float(results_delta_z[best_delta_z]['hit_rate_high_z'])
        },
        'binary_best': {
            'model': results_binary[best_binary]['name'],
            'accuracy_test': float(results_binary[best_binary]['accuracy_test']),
            'accuracy_high_z': float(results_binary[best_binary]['accuracy_high_z'])
        }
    }
}

with open(results_dir / 'layer2_recommendation.json', 'w') as f:
    json.dump(recommendation, f, indent=2)

print(f"\n✓ Saved recommendation: {results_dir / 'layer2_recommendation.json'}")

print("\n" + "="*80)
print("✅ LAYER 2 EVALUATION COMPLETE")
print("="*80)
print(f"\nOutput files saved to: {results_dir.absolute()}")
print(f"\nNote: If a simple model (Ridge/ElasticNet) wins, that's GOOD!")
print(f"      Simple models are often more robust for pressure signals.")

