# FX Two-Layer Framework - Quick Start Guide

## Overview

A proper two-layer EURUSD valuation framework with empirical model selection:

- **Layer 1 (Monthly)**: Macro fundamentals → Fair Value + Regime
- **Layer 2 (Weekly)**: Market pressure → Expanding/Compressing signal
- **Integration**: Narrative synthesis (NOT mathematical blending)

## Quick Start (ONE COMMAND)

```bash
python fx_two_layer_master_runner.py
```

This runs the entire pipeline:
1. Layer 1: Data → Features → 5 Models → Evaluation → Selection
2. Layer 2: Data → Features → 8 Models (2 targets × 4 models) → Evaluation → Selection
3. Final Summary with recommendations

**Expected Runtime**: 5-10 minutes (depending on data fetching)

## Manual Step-by-Step (Optional)

If you prefer to run step-by-step:

### Layer 1 (Monthly Macro Valuation)

```bash
# 1. Build monthly dataset
python eurusd_v2_monthly_build.py

# 2. Engineer features
python eurusd_v2_monthly_features.py

# 3. Train models (Ridge, Lasso, ElasticNet, XGBoost, Two-Stage)
python fx_layer1_monthly_valuation.py

# 4. Evaluate and select best model
python fx_layer1_evaluation_dashboard.py
```

**Output**: `fx_layer1_outputs/` with predictions, charts, and `layer1_recommendation.json`

### Layer 2 (Weekly Pressure Signal)

```bash
# 1. Build weekly dataset
python fx_layer2_weekly_data.py

# 2. Engineer features
python fx_layer2_weekly_features.py

# 3. Train models (Ridge, ElasticNet, XGBoost, LightGBM × 2 targets)
python fx_layer2_pressure_model.py

# 4. Evaluate and select best model
python fx_layer2_evaluation_dashboard.py
```

**Output**: `fx_layer2_outputs/` with predictions, charts, and `layer2_recommendation.json`

### Final Summary

```bash
python fx_two_layer_summary.py
```

**Output**: `fx_two_layer_summary.json` + framework diagram

## Key Evaluation Criteria

### Layer 1 (Monthly Fair Value)

**Priority Order**:
1. ✅ Test R² (generalization)
2. ✅ Regime frequency (should be ~68% in-line, ~27% stretch, ~5% break)
3. ✅ FV stability (smooth, not jumpy)
4. RMSE (secondary)
5. R² (informational only)

**What wins**: Often Ridge or Lasso (simple is good!)

### Layer 2 (Weekly Pressure)

**Priority Order**:
1. ✅ Hit rate / Accuracy (test set)
2. ✅ Hit rate when |mispricing| > 1σ (stretched regime)
3. Directional consistency

**Two Target Options**:
- **Δz**: Predicts change in mispricing z-score (magnitude)
- **Binary**: Predicts expanding (1) vs compressing (0) (direction)

**What wins**: Model with best hit rate in stretched regimes

## Model Options

### Layer 1 Models Tested
1. **Ridge Baseline** - L2 regularization
2. **Lasso** - L1 regularization (feature selection)
3. **ElasticNet** - L1 + L2 regularization
4. **XGBoost Single-Stage** - Regularized tree ensemble
5. **Two-Stage (Ridge + XGBoost)** - Base model + residual correction

### Layer 2 Models Tested (per target)
1. **Ridge** - Simple linear baseline
2. **ElasticNet** - L1 + L2 regularization
3. **XGBoost** - Tree ensemble
4. **LightGBM** - Faster tree ensemble

Total: 4 models × 2 targets = 8 model variants

## Output Files

### Layer 1 Outputs
```
fx_layer1_outputs/
├── all_models.pkl                    # All trained models
├── evaluation_summary.json           # Metrics comparison
├── layer1_recommendation.json        # Selected model
├── ridge_predictions.csv             # Predictions per model
├── lasso_predictions.csv
├── elasticnet_predictions.csv
├── xgboost_single_predictions.csv
├── twostage_predictions.csv
├── layer1_comparison_fv.png          # Charts
├── layer1_comparison_regimes.png
└── layer1_comparison_stability.png
```

### Layer 2 Outputs
```
fx_layer2_outputs/
├── all_models.pkl                    # All trained models
├── evaluation_summary.json           # Metrics comparison
├── layer2_recommendation.json        # Selected model + target
├── layer2_comparison_delta_z.png     # Charts
└── layer2_comparison_binary.png
```

### Final Summary
```
fx_two_layer_summary.json             # Complete framework spec
fx_two_layer_framework_diagram.png    # Visual diagram
```

## Integration with FX Views Page

The framework feeds into your Streamlit FX Views page:

1. **Section 1 (Fair Value & Regime)**: Use Layer 1 predictions
2. **Section 2 (Macro Drivers)**: Extract from Layer 1 feature importances
3. **Section 3 (Technical)**: Separate module (weekly bars)
4. **Section 4 (Reference Levels)**: Context only (Fibonacci, highs/lows)
5. **Section 5 (Historical Context)**: State-based analogue matching
6. **Section 6 (Nikhil View)**: AI synthesis using L1 + L2 + technicals

## Important Philosophy

### If Ridge Wins, That's GOOD!

If the evaluation selects:
- Layer 1: Ridge
- Layer 2: Ridge (Δz target)

**This is an excellent outcome**, not a disappointment.

**Why?**
- ✅ Simple models are more stable
- ✅ More interpretable (can explain to clients)
- ✅ Less prone to overfitting
- ✅ Easier to maintain
- ✅ Faster to retrain

**When complex models win:**
- Only if they SIGNIFICANTLY outperform on test set
- AND show stable regime distributions
- AND maintain economic interpretability

## Retraining

To retrain with fresh data:

```bash
# Quick retrain (keeps old data files, just retrains models)
python fx_layer1_monthly_valuation.py
python fx_layer1_evaluation_dashboard.py
python fx_layer2_pressure_model.py
python fx_layer2_evaluation_dashboard.py

# Full refresh (fetches new data)
rm *.pkl  # Delete cached data
python fx_two_layer_master_runner.py
```

## Troubleshooting

### Issue: "Layer 1 recommendation not found"

**Solution**: Run Layer 1 pipeline first
```bash
python fx_layer1_monthly_valuation.py
python fx_layer1_evaluation_dashboard.py
```

### Issue: "Weekly data forward-fill errors"

**Solution**: Layer 2 needs Layer 1 to map monthly FV to weekly. Ensure Layer 1 is complete first.

### Issue: "FRED API rate limiting"

**Solution**: The `data_fetcher.py` should handle this. If issues persist, add delays between requests.

## Next Steps

After running the framework:

1. **Review recommendations**:
   - Open `fx_layer1_outputs/layer1_recommendation.json`
   - Open `fx_layer2_outputs/layer2_recommendation.json`
   - Read `fx_two_layer_summary.json`

2. **View charts**:
   - Layer 1 comparison charts in `fx_layer1_outputs/`
   - Layer 2 comparison charts in `fx_layer2_outputs/`
   - Framework diagram: `fx_two_layer_framework_diagram.png`

3. **Update FX Views page**:
   - Load selected Layer 1 model predictions
   - Integrate Layer 2 pressure signal
   - Update narrative synthesis logic

4. **Deploy to Streamlit Cloud** (when ready):
   - Copy selected model files
   - Update `pages/3_🌍_FX_Views.py` to use new framework
   - Test locally first: `streamlit run dashboard_regional.py`

## Questions?

The framework is designed to be:
- ✅ Empirically rigorous
- ✅ Simple when simple works
- ✅ Interpretable and explainable
- ✅ Production-ready

If Ridge wins both layers → celebrate! Simple models that work are the best models.


