# FX Two-Layer Valuation Framework

**Objective**: Build a robust, empirically-validated two-layer EURUSD framework that selects the best model for each layer based on its purpose, not complexity.

## Philosophy

> **"If Layer 1 best = simple Ridge and Layer 2 best = XGBoost, that is a very good outcome, not a disappointment."**

This framework embraces simplicity when it works. Complex models are only better if they:
- Significantly outperform on test set
- Show stable regime distributions
- Maintain economic interpretability

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                 LAYER 1: MONTHLY MACRO VALUATION              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Data: Monthly yields, inflation, credit, labor, liq.  │  │
│  │  Models: Ridge | Lasso | ElasticNet | XGBoost | 2-Stage│  │
│  │  Evaluation: Stability, Regime Freq, Interpretability  │  │
│  │  Output: Fair Value + Mispricing Z + Regime Label      │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                                 ↓
┌───────────────────────────────────────────────────────────────┐
│               LAYER 2: WEEKLY PRESSURE SIGNAL                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Data: Weekly yields, credit, vol (VIX), liquidity     │  │
│  │  Models: Ridge | ElasticNet | XGBoost | LightGBM       │  │
│  │  Targets: Δz (change) OR Binary (expand/compress)      │  │
│  │  Evaluation: Hit Rate, Directional Accuracy            │  │
│  │  Output: Pressure signal on mispricing                 │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                                 ↓
┌───────────────────────────────────────────────────────────────┐
│                    NARRATIVE SYNTHESIS                        │
│  (NOT mathematical blending - layers inform judgment)         │
└───────────────────────────────────────────────────────────────┘
```

## Quick Start

**Run entire pipeline** (5-10 minutes):
```bash
python fx_two_layer_master_runner.py
```

**Check current recommendations**:
```bash
python fx_check_recommendations.py
```

## Layer 1: Monthly Macro Valuation

### Purpose
Provide a stable, macro-anchored fair value estimate based on slow-moving fundamentals.

### Data (Monthly Frequency)
- **US & EA Yields**: 1Y, 10Y, TIPS
- **Inflation**: CPI, HICP (YoY)
- **Credit Spreads**: US HY, BBB; EA HY
- **Liquidity**: Fed RRP
- **Labor**: US unemployment

### Models Tested
1. **Ridge**: L2 regularization baseline
2. **Lasso**: L1 regularization (feature selection)
3. **ElasticNet**: L1 + L2 regularization
4. **XGBoost Single-Stage**: Regularized tree ensemble
5. **Two-Stage**: Base model (Ridge) + Residual correction (XGBoost)

### Evaluation Criteria (Ranked)
1. **Stability & Interpretability**: Smooth FV, low change volatility
2. **Reasonable Regime Frequency**: ~68% in-line, ~27% stretch, ~5% break
3. **Economic Coherence**: Features make sense
4. **RMSE**: Secondary (error magnitude)
5. **R²**: Informational only

### Outputs
- Monthly fair value
- Mispricing (spot - FV)
- Mispricing z-score (σ from training)
- Regime label (In-line / Stretch / Break)

### Files
```
eurusd_v2_monthly_build.py            # Build monthly dataset
eurusd_v2_monthly_features.py         # Engineer features
fx_layer1_monthly_valuation.py        # Train 5 models
fx_layer1_evaluation_dashboard.py     # Evaluate & select
```

## Layer 2: Weekly Pressure Signal

### Purpose
Detect weekly market-driven pressure on mispricing for tactical timing edge.

### Data (Weekly Frequency)
- **Market Yields**: US & EA (1Y, 2Y, 10Y)
- **Credit Spreads**: US & EA HY, BBB
- **Volatility**: VIX, VXEEM (weekly mean)
- **Liquidity**: Fed RRP
- **FX Momentum**: Returns, MAs, volatility

**Excluded**: Monthly macro releases (CPI, unemployment, etc.)

### Target Options
1. **Δz (Regression)**: Change in mispricing z-score
   - Pro: Captures magnitude
   - Con: Harder to interpret
   
2. **Binary (Classification)**: Expanding (1) vs Compressing (0)
   - Pro: Simple signal
   - Con: Loses magnitude

### Models Tested (per target)
1. **Ridge**: Linear baseline
2. **ElasticNet**: L1 + L2 regularization
3. **XGBoost**: Tree ensemble
4. **LightGBM**: Fast tree ensemble

**Total**: 4 models × 2 targets = 8 variants

### Evaluation Criteria
1. **Hit Rate / Accuracy**: Test set performance
2. **Conditional Performance**: When |mispricing| > 1σ
3. **Directional Consistency**

### Outputs
- Weekly pressure signal
- Direction (expanding / compressing)
- Optional: Magnitude (if Δz target selected)

### Files
```
fx_layer2_weekly_data.py              # Build weekly dataset
fx_layer2_weekly_features.py          # Engineer features
fx_layer2_pressure_model.py           # Train 8 models (2 targets × 4)
fx_layer2_evaluation_dashboard.py     # Evaluate & select
```

## Integration & Usage

### How Layers Work Together

**Layer 1 (Monthly)** provides:
- Fair value estimate
- Current mispricing magnitude (z-score)
- Regime classification

**Layer 2 (Weekly)** provides:
- Pressure direction on mispricing
- Leading indicator of mean reversion vs momentum

**Narrative Synthesis** (NOT mathematical blending):
- Overvalued + Expanding pressure → Bearish
- Undervalued + Compressing pressure → Bullish
- Overvalued + Compressing pressure → Potential reversal
- Undervalued + Expanding pressure → Continued weakness

### FX Views Page Integration

The framework feeds into your Streamlit FX Views page:

1. **Fair Value & Regime**: Layer 1 monthly predictions
2. **Macro Drivers**: Layer 1 feature analysis (differentials + percentiles)
3. **Technical Conditions**: Separate weekly technical module
4. **Key Reference Levels**: Context only (Fibonacci, highs/lows)
5. **Historical Context**: State-based analogue matching
6. **Nikhil FX View**: AI synthesis of all components

## File Structure

```
.
├── README_FX_TWO_LAYER_FRAMEWORK.md (this file)
├── FX_TWO_LAYER_QUICKSTART.md (quick guide)
├── fx_two_layer_master_runner.py (run all)
├── fx_check_recommendations.py (view current state)
│
├── Layer 1 (Monthly)
│   ├── eurusd_v2_monthly_build.py
│   ├── eurusd_v2_monthly_features.py
│   ├── fx_layer1_monthly_valuation.py
│   └── fx_layer1_evaluation_dashboard.py
│
├── Layer 2 (Weekly)
│   ├── fx_layer2_weekly_data.py
│   ├── fx_layer2_weekly_features.py
│   ├── fx_layer2_pressure_model.py
│   └── fx_layer2_evaluation_dashboard.py
│
├── Summary
│   └── fx_two_layer_summary.py
│
└── Outputs
    ├── fx_layer1_outputs/
    │   ├── all_models.pkl
    │   ├── evaluation_summary.json
    │   ├── layer1_recommendation.json
    │   ├── *_predictions.csv (per model)
    │   └── *.png (charts)
    │
    ├── fx_layer2_outputs/
    │   ├── all_models.pkl
    │   ├── evaluation_summary.json
    │   ├── layer2_recommendation.json
    │   └── *.png (charts)
    │
    ├── fx_two_layer_summary.json
    └── fx_two_layer_framework_diagram.png
```

## Retraining Schedule

### Full Refresh (Monthly)
- Fetches fresh data from FRED & ECB
- Rebuilds features
- Retrains all models
- Re-evaluates

```bash
rm *.pkl  # Clear cached data
python fx_two_layer_master_runner.py
```

### Quick Retrain (As Needed)
- Uses cached data
- Retrains models only
- Useful for hyperparameter tuning

```bash
python fx_layer1_monthly_valuation.py
python fx_layer1_evaluation_dashboard.py
python fx_layer2_pressure_model.py
python fx_layer2_evaluation_dashboard.py
python fx_two_layer_summary.py
```

## Model Selection Logic

### Layer 1 Scoring System
- **R² (40 pts)**: Test set generalization
- **Regime Frequency (30 pts)**: Distance from ideal (68%, 27%, 5%)
- **Stability (20 pts)**: FV change volatility
- **RMSE (10 pts)**: Error magnitude

**Winner**: Highest total score

### Layer 2 Scoring System
- **Hit Rate / Accuracy (60%)**: Overall test performance
- **Conditional Performance (40%)**: Performance when |z| > 1σ

**Winner**: Best weighted score

### Important: Simple Often Wins
- Ridge often beats complex models
- This is GOOD, not bad
- Simple = stable, interpretable, maintainable

## Key Design Decisions

### Why Two Layers?
- **Monthly**: Stable macro anchor (slow-moving fundamentals)
- **Weekly**: Tactical pressure signal (market-driven)
- **Separation**: Different frequencies, different purposes

### Why NOT Blend Mathematically?
- Layers serve different purposes
- Blending destroys interpretability
- Narrative synthesis preserves judgment

### Why Test Multiple Models?
- Empirical validation beats assumptions
- Let data decide what works
- Simple often wins (and that's fine!)

### Why These Evaluation Criteria?
- Layer 1: Stability matters more than fit
- Layer 2: Direction matters more than magnitude
- Both: Interpretability is crucial

## FAQ

**Q: What if Ridge wins both layers?**  
A: **Celebrate!** Simple models that work are the best models. They're stable, interpretable, and easy to maintain.

**Q: Can I use XGBoost if it loses to Ridge?**  
A: Only if you have a good reason (e.g., you value magnitude over stability). The evaluation selects based on purpose, not complexity.

**Q: How often should I retrain?**  
A: Monthly full refresh for new data. Weekly quick retrain is optional if you want more responsive models.

**Q: Can I add more features?**  
A: Yes! Add to `*_features.py` scripts. Rerun feature engineering and model training.

**Q: Can I change evaluation criteria?**  
A: Yes! Adjust weights in `*_evaluation_dashboard.py` scripts based on your priorities.

**Q: Why not daily frequency?**  
A: Weekly balances granularity with stability. Daily is too noisy for macro signals.

## Technical Notes

### Dependencies
- pandas, numpy
- scikit-learn (Ridge, Lasso, ElasticNet)
- xgboost, lightgbm
- matplotlib (charts)
- data_fetcher.py (FRED API wrapper)

### Data Sources
- **FRED**: US macro, yields, credit
- **ECB**: Eurozone yields (CSV)
- **Yahoo Finance**: FX spot (via dashboard)

### Performance
- Full pipeline: ~5-10 minutes (includes data fetching)
- Layer 1 only: ~2-3 minutes
- Layer 2 only: ~3-4 minutes
- Check recommendations: Instant

## Deployment

### For Production (Streamlit Cloud)
1. Run full pipeline locally
2. Export selected model files
3. Update FX Views page to load models
4. Test locally: `streamlit run dashboard_regional.py`
5. Deploy to Streamlit Cloud
6. Set up monthly retraining schedule

### Model Files to Export
- `fx_layer1_outputs/<selected_model>_predictions.csv`
- `fx_layer2_outputs/layer2_recommendation.json`
- `fx_two_layer_summary.json`

## Support

For questions or issues:
1. Check `FX_TWO_LAYER_QUICKSTART.md`
2. Run `python fx_check_recommendations.py`
3. Review output charts in `fx_layer*_outputs/`

## License & Attribution

This framework is designed for Nikhil's FX Views dashboard. Methodology:
- Layer 1: Macro fundamentals valuation (standard approach)
- Layer 2: Market pressure signal (custom design)
- Evaluation: Purpose-driven criteria (not just RMSE)

---

**Remember**: The goal is not the most complex model. The goal is the best model for the job. Often, that's the simplest one that works.


