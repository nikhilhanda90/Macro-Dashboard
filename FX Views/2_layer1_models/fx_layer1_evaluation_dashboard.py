"""
FX LAYER 1 - MODEL EVALUATION DASHBOARD
Compare all monthly models on proper criteria for fair value estimation
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

print("="*80)
print("FX LAYER 1 - EVALUATION DASHBOARD")
print("="*80)

# Load results
results_dir = Path('fx_layer1_outputs')
with open(results_dir / 'all_models.pkl', 'rb') as f:
    all_models = pickle.load(f)

with open(results_dir / 'evaluation_summary.json', 'r') as f:
    eval_summary = json.load(f)

print("\n✓ Loaded results for 5 models\n")

# ============================================================================
# COMPARISON TABLE
# ============================================================================

print("="*80)
print("LAYER 1 MODEL COMPARISON")
print("="*80)
print("\nEvaluation Criteria (in priority order):")
print("  1. Test R² (generalization)")
print("  2. Regime frequency (should be reasonable: ~68% in-line, ~27% stretch, ~5% break)")
print("  3. FV stability (smooth, not jumpy)")
print("  4. RMSE (error magnitude)")
print("  5. Economic interpretability (feature count & coherence)")
print("\n" + "-"*80)

# Create comparison dataframe
comparison_data = []
for key in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']:
    model = all_models[key]
    summary = eval_summary[key]
    
    row = {
        'Model': model['name'],
        'R² Test': summary['r2_test'] if summary['r2_test'] is not None else np.nan,
        'RMSE Test': summary['rmse_test'] if summary['rmse_test'] is not None else np.nan,
        'σ (Training)': summary['sigma'],
        'In-line %': summary['regime_train']['in_line_pct'] * 100,
        'Stretch %': summary['regime_train']['stretch_pct'] * 100,
        'Break %': summary['regime_train']['break_pct'] * 100,
        'FV Avg Change': summary['stability']['mean_abs_change'],
        'FV Max Jump': summary['stability']['max_monthly_jump'],
        'FV Change Vol': summary['stability']['change_std']
    }
    comparison_data.append(row)

df_comparison = pd.DataFrame(comparison_data)

# Print comprehensive table
print("\n" + "="*130)
print("COMPREHENSIVE MODEL COMPARISON TABLE")
print("="*130)
print(f"\n{'Model':<30} {'R²Test':>8} {'RMSE':>10} {'σ':>10} {'In-line':>9} {'Stretch':>9} {'Break':>8} {'AvgΔ':>10} {'MaxJump':>10}")
print("-" * 130)
for _, row in df_comparison.iterrows():
    print(f"{row['Model']:<30} "
          f"{row['R² Test']:>8.3f} "
          f"{row['RMSE Test']:>10.5f} "
          f"{row['σ (Training)']:>10.5f} "
          f"{row['In-line %']:>8.1f}% "
          f"{row['Stretch %']:>8.1f}% "
          f"{row['Break %']:>7.1f}% "
          f"{row['FV Avg Change']:>10.5f} "
          f"{row['FV Max Jump']:>10.5f}")
print("-" * 130)

# Legend
print("\nColumn Definitions:")
print("  R²Test:   Out-of-sample R² (higher is better, but watch for overfitting)")
print("  RMSE:     Root mean squared error on test set (lower is better)")
print("  σ:        Training residual standard deviation (used for z-scores)")
print("  In-line:  % of time |mispricing| < 1σ (ideal ~68%)")
print("  Stretch:  % of time 1σ ≤ |mispricing| < 2σ (ideal ~27%)")
print("  Break:    % of time |mispricing| ≥ 2σ (ideal ~5%)")
print("  AvgΔ:     Mean absolute monthly change in FV (lower = more stable)")
print("  MaxJump:  Largest single-month FV jump (lower = more stable)")
print("="*130)

# ============================================================================
# SCORING SYSTEM
# ============================================================================

print("\n" + "="*80)
print("AUTOMATED SCORING (for guidance)")
print("="*80)

scores = {}
for key in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']:
    summary = eval_summary[key]
    
    # Criteria 1: Test R² (40 points max)
    r2_test = summary['r2_test'] if summary['r2_test'] is not None else 0
    r2_score = max(0, min(40, r2_test * 100))  # Cap at 40
    
    # Criteria 2: Regime frequency (30 points)
    # Ideal: ~68% in-line, ~27% stretch, ~5% break
    in_line = summary['regime_train']['in_line_pct']
    stretch = summary['regime_train']['stretch_pct']
    break_pct = summary['regime_train']['break_pct']
    
    regime_score = 30 - (
        abs(in_line - 0.68) * 100 +  # Penalize deviation from 68%
        abs(stretch - 0.27) * 100 +  # Penalize deviation from 27%
        abs(break_pct - 0.05) * 100  # Penalize deviation from 5%
    )
    regime_score = max(0, regime_score)
    
    # Criteria 3: Stability (20 points)
    # Lower FV change vol is better
    change_vol = summary['stability']['change_std']
    stability_score = max(0, 20 - change_vol * 1000)  # Scaled penalty
    
    # Criteria 4: RMSE (10 points)
    rmse = summary['rmse_test'] if summary['rmse_test'] is not None else 1.0
    rmse_score = max(0, 10 - rmse * 200)  # Scaled penalty
    
    total_score = r2_score + regime_score + stability_score + rmse_score
    
    scores[key] = {
        'r2_score': r2_score,
        'regime_score': regime_score,
        'stability_score': stability_score,
        'rmse_score': rmse_score,
        'total_score': total_score
    }

# Print scores
print(f"\n{'Model':<40} {'R² (40)':>10} {'Regime (30)':>12} {'Stab (20)':>12} {'RMSE (10)':>12} {'TOTAL':>10}")
print("-" * 105)
for key in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']:
    model_name = all_models[key]['name']
    s = scores[key]
    print(f"{model_name:<40} {s['r2_score']:>10.1f} {s['regime_score']:>12.1f} {s['stability_score']:>12.1f} {s['rmse_score']:>12.1f} {s['total_score']:>10.1f}")

# Find winner
best_model_key = max(scores.keys(), key=lambda k: scores[k]['total_score'])
best_model = all_models[best_model_key]

print("\n" + "="*80)
print(f"🏆 RECOMMENDED MODEL: {best_model['name'].upper()}")
print("="*80)
print(f"\nScore: {scores[best_model_key]['total_score']:.1f}/100")
print(f"Test R²: {eval_summary[best_model_key]['r2_test']:.3f}")
print(f"RMSE: {eval_summary[best_model_key]['rmse_test']:.5f}")
print(f"Training σ: {eval_summary[best_model_key]['sigma']:.5f}")
print(f"\nRegime Distribution:")
print(f"  In-line (<1σ):  {eval_summary[best_model_key]['regime_train']['in_line_pct']:.1%}")
print(f"  Stretch (1-2σ): {eval_summary[best_model_key]['regime_train']['stretch_pct']:.1%}")
print(f"  Break (>2σ):    {eval_summary[best_model_key]['regime_train']['break_pct']:.1%}")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "="*80)
print("GENERATING COMPARISON CHARTS")
print("="*80)

# Chart 1: Fair Value Comparison (2020+)
fig, axes = plt.subplots(3, 2, figsize=(16, 14))
fig.suptitle('Layer 1 Model Comparison - Fair Value Estimates (2020+)', 
             fontsize=16, fontweight='bold', color='white')

for idx, key in enumerate(['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']):
    ax = axes[idx // 2, idx % 2]
    
    # Load predictions
    pred_df = pd.read_csv(results_dir / f'{key}_predictions.csv', parse_dates=['date'])
    pred_df = pred_df[pred_df['date'] >= '2020-01-01']
    
    model_name = all_models[key]['name']
    sigma = all_models[key]['sigma']
    
    # Plot bands
    ax.fill_between(pred_df['date'], pred_df['fv_minus_2sigma'], pred_df['fv_plus_2sigma'],
                     alpha=0.15, color='gray', label='±2σ')
    ax.fill_between(pred_df['date'], pred_df['fv_minus_1sigma'], pred_df['fv_plus_1sigma'],
                     alpha=0.25, color='lightblue', label='±1σ')
    
    # Plot FV and spot
    ax.plot(pred_df['date'], pred_df['fair_value'], '--', color='blue', linewidth=1.5, label='Fair Value')
    ax.plot(pred_df['date'], pred_df['spot'], '-', color='black', linewidth=2, label='Spot')
    
    # Mark test period
    ax.axvline(pd.Timestamp('2025-01-01'), color='red', linestyle=':', alpha=0.5, linewidth=1)
    
    # Styling
    ax.set_title(f"{model_name} (R²={eval_summary[key]['r2_test']:.3f})", 
                fontsize=11, fontweight='bold', color='white')
    ax.set_ylabel('EURUSD', fontsize=9, color='white')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#0a0a0a')
    ax.tick_params(colors='white', labelsize=8)
    
    # Color spines
    for spine in ax.spines.values():
        spine.set_color('white')

# Remove extra subplot
axes[2, 1].remove()

# Add recommendation text in empty space
fig.text(0.72, 0.22, f"🏆 RECOMMENDED\n\n{best_model['name']}\n\nScore: {scores[best_model_key]['total_score']:.0f}/100\nR²: {eval_summary[best_model_key]['r2_test']:.3f}",
         fontsize=14, fontweight='bold', color='#00ff80',
         bbox=dict(boxstyle='round,pad=1', facecolor='black', edgecolor='#00ff80', linewidth=2),
         ha='center', va='center')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(results_dir / 'layer1_comparison_fv.png', dpi=300, facecolor='#0a0a0a')
plt.close()
print(f"✓ Saved: {results_dir / 'layer1_comparison_fv.png'}")

# Chart 2: Regime Distribution Comparison
fig, ax = plt.subplots(figsize=(12, 7))
fig.suptitle('Layer 1 Model Comparison - Regime Distribution (Training Period)',
             fontsize=14, fontweight='bold', color='white')

model_names = [all_models[k]['name'] for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]
in_line = [eval_summary[k]['regime_train']['in_line_pct'] * 100 for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]
stretch = [eval_summary[k]['regime_train']['stretch_pct'] * 100 for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]
break_pct = [eval_summary[k]['regime_train']['break_pct'] * 100 for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]

x = np.arange(len(model_names))
width = 0.25

bars1 = ax.bar(x - width, in_line, width, label='In-line (<1σ)', color='green', alpha=0.8)
bars2 = ax.bar(x, stretch, width, label='Stretch (1-2σ)', color='yellow', alpha=0.8)
bars3 = ax.bar(x + width, break_pct, width, label='Break (>2σ)', color='red', alpha=0.8)

# Add ideal reference lines
ax.axhline(68, color='green', linestyle='--', alpha=0.5, linewidth=1, label='Ideal In-line (68%)')
ax.axhline(27, color='yellow', linestyle='--', alpha=0.5, linewidth=1, label='Ideal Stretch (27%)')
ax.axhline(5, color='red', linestyle='--', alpha=0.5, linewidth=1, label='Ideal Break (5%)')

ax.set_ylabel('Percentage (%)', fontsize=11, color='white')
ax.set_xticks(x)
ax.set_xticklabels(model_names, rotation=15, ha='right', fontsize=9, color='white')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
ax.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')

for spine in ax.spines.values():
    spine.set_color('white')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig(results_dir / 'layer1_comparison_regimes.png', dpi=300, facecolor='#0a0a0a')
plt.close()
print(f"✓ Saved: {results_dir / 'layer1_comparison_regimes.png'}")

# Chart 3: Stability Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Layer 1 Model Comparison - Fair Value Stability',
             fontsize=14, fontweight='bold', color='white')

# Mean absolute change
mean_changes = [eval_summary[k]['stability']['mean_abs_change'] for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]
ax1.barh(model_names, mean_changes, color='cyan', alpha=0.7)
ax1.set_xlabel('Mean Absolute Monthly Change', fontsize=10, color='white')
ax1.set_title('Lower is Better (Smoother FV)', fontsize=11, color='white')
ax1.grid(True, alpha=0.3, axis='x')
ax1.set_facecolor('#0a0a0a')
ax1.tick_params(colors='white', labelsize=9)
for spine in ax1.spines.values():
    spine.set_color('white')

# Change volatility
change_vols = [eval_summary[k]['stability']['change_std'] for k in ['ridge', 'lasso', 'elasticnet', 'xgboost_single', 'twostage']]
ax2.barh(model_names, change_vols, color='orange', alpha=0.7)
ax2.set_xlabel('FV Change Volatility (Std Dev)', fontsize=10, color='white')
ax2.set_title('Lower is Better (More Stable)', fontsize=11, color='white')
ax2.grid(True, alpha=0.3, axis='x')
ax2.set_facecolor('#0a0a0a')
ax2.tick_params(colors='white', labelsize=9)
for spine in ax2.spines.values():
    spine.set_color('white')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig(results_dir / 'layer1_comparison_stability.png', dpi=300, facecolor='#0a0a0a')
plt.close()
print(f"✓ Saved: {results_dir / 'layer1_comparison_stability.png'}")

# ============================================================================
# SAVE RECOMMENDATION
# ============================================================================

recommendation = {
    'selected_model': best_model_key,
    'model_name': best_model['name'],
    'score': float(scores[best_model_key]['total_score']),
    'metrics': {
        'r2_test': float(eval_summary[best_model_key]['r2_test']) if eval_summary[best_model_key]['r2_test'] is not None else None,
        'rmse_test': float(eval_summary[best_model_key]['rmse_test']) if eval_summary[best_model_key]['rmse_test'] is not None else None,
        'sigma': float(eval_summary[best_model_key]['sigma'])
    },
    'regime_distribution': eval_summary[best_model_key]['regime_train'],
    'stability': eval_summary[best_model_key]['stability']
}

with open(results_dir / 'layer1_recommendation.json', 'w') as f:
    json.dump(recommendation, f, indent=2)

print(f"\n✓ Saved recommendation: {results_dir / 'layer1_recommendation.json'}")

print("\n" + "="*80)
print("✅ LAYER 1 EVALUATION COMPLETE")
print("="*80)
print(f"\nRecommended Model: {best_model['name']}")
print(f"Output files saved to: {results_dir.absolute()}")
print(f"\nNote: If Ridge or Lasso wins, that's a GOOD outcome!")
print(f"      Simple, interpretable models are often best for fair value.")

