# FX Two-Layer Framework - White Paper Package

## 📚 Complete Documentation Index

Welcome to the comprehensive technical documentation for the FX Two-Layer Valuation Framework. This package contains everything you need to understand, implement, and deploy the models.

---

## 🎯 Quick Navigation

### Core Documentation
1. **[FX_LAYER1_WHITE_PAPER.md](./FX_LAYER1_WHITE_PAPER.md)** - Monthly Macro Valuation
2. **[FX_LAYER2_WHITE_PAPER.md](./FX_LAYER2_WHITE_PAPER.md)** - Weekly Pressure Signal
3. **[README_FX_TWO_LAYER_FRAMEWORK.md](./README_FX_TWO_LAYER_FRAMEWORK.md)** - System Overview
4. **[FX_TWO_LAYER_QUICKSTART.md](./FX_TWO_LAYER_QUICKSTART.md)** - Getting Started Guide

### Data Files
5. **fx_layer1_elasticnet_coefficients_full.csv** - All Layer 1 coefficients (112 features)
6. **fx_layer1_all_models_comparison.csv** - Layer 1 model comparison table
7. **fx_layer2_xgboost_importances_full.csv** - Layer 2 feature importances
8. **fx_layer2_all_models_comparison.csv** - Layer 2 model comparison table
9. **fx_models_input_output_summary.json** - Input/output specifications

### Visualizations
10. **fx_2025_spot_vs_predicted.png** - Layer 1: 2025 Fair Value Chart
11. **fx_two_layer_framework_diagram.png** - System Architecture Diagram
12. **fx_layer2_summary_table.txt** - Layer 2: Weekly Results Table

### Model Artifacts
13. **fx_layer1_outputs/** - Layer 1 trained models & predictions
14. **fx_layer2_outputs/** - Layer 2 trained models & predictions
15. **fx_two_layer_summary.json** - Complete framework specification

---

## 📖 Reading Guide

### For Executive Summary (5 minutes)
1. Read **Executive Summary** sections in both white papers
2. View **fx_two_layer_framework_diagram.png**
3. Check **fx_two_layer_summary.json**

### For Technical Understanding (30 minutes)
1. **FX_LAYER1_WHITE_PAPER.md** - Sections 1-5 (Model selection, coefficients, inputs)
2. **FX_LAYER2_WHITE_PAPER.md** - Sections 1-5 (Model selection, importances, signals)
3. Review coefficient/importance CSV files

### For Implementation (1 hour)
1. **FX_TWO_LAYER_QUICKSTART.md** - Setup & running
2. **FX_LAYER1_WHITE_PAPER.md** - Section 7 (Technical Implementation)
3. **FX_LAYER2_WHITE_PAPER.md** - Section 8 (Technical Implementation)
4. **fx_models_input_output_summary.json** - API specifications

### For Full Deep Dive (2+ hours)
Read everything in order:
1. README → Quickstart → Layer 1 White Paper → Layer 2 White Paper
2. Examine all CSV data files
3. Review model artifacts in output folders
4. Study visualizations

---

## 🎓 What Each Document Contains

### FX_LAYER1_WHITE_PAPER.md (Monthly Valuation)
**42 pages** of comprehensive Layer 1 documentation:

- ✅ Model selection process (5 models tested)
- ✅ Complete ElasticNet specification (α, L1 ratio, intercept)
- ✅ All 112 feature coefficients with interpretations
- ✅ Input categories (rates, credit, inflation, labor, vol, liquidity)
- ✅ Feature engineering pipeline (lags, changes, z-scores)
- ✅ 2025 out-of-sample performance analysis
- ✅ Regime distribution analysis
- ✅ Stability metrics
- ✅ Implementation guide
- ✅ Strengths, limitations, use cases
- ✅ Comparison with other models

**Key Findings**:
- **Winner**: ElasticNet (R² = 0.455, ideal regime distribution)
- **Selected Features**: 27 out of 112
- **Top Driver**: 1Y rate differential (-0.014448 coefficient)
- **Stability**: Mean monthly change = 0.01066 (very smooth)

### FX_LAYER2_WHITE_PAPER.md (Weekly Pressure)
**38 pages** of comprehensive Layer 2 documentation:

- ✅ Model selection process (6 variants tested)
- ✅ Complete XGBoost specification (200 trees, depth=3)
- ✅ Feature importance rankings (~180 features)
- ✅ Input categories (rates, credit, vol, FX momentum)
- ✅ Trading signal interpretation logic
- ✅ 11-week test period analysis (2025)
- ✅ Weekly prediction accuracy (81.8%)
- ✅ Performance when stretched (85.7%)
- ✅ Integration with Layer 1
- ✅ Trade setup examples
- ✅ Implementation guide

**Key Findings**:
- **Winner**: XGBoost Δz (81.8% hit rate)
- **Top Driver**: 4-week FX momentum (0.1234 importance)
- **Strength**: 85.7% accuracy when |z| > 1σ
- **Weakness**: 2 misses in momentum continuation phases

---

## 📊 Key Results Summary

### Layer 1 (Monthly Fair Value)
```
Model: ElasticNet
Test R²: 0.455
RMSE: 0.03741
Regime Distribution: 65% in-line, 31% stretch, 4% break ✅
Feature Selection: 27/112 features
Stability: Excellent (smooth FV evolution)
```

### Layer 2 (Weekly Pressure)
```
Model: XGBoost (Δz target)
Hit Rate (overall): 81.8% (9/11 weeks)
Hit Rate (|z|>1σ): 85.7% (6/7 weeks) ⭐
RMSE: 0.3142
Top Feature: 4-week FX momentum
Strength: Mean reversion in stretched regimes
```

### Combined Framework
```
Layer 1 provides: WHERE (monthly fair value anchor)
Layer 2 provides: WHICH WAY (weekly pressure direction)
Result: Strategic + Tactical = Complete FX view
```

---

## 🔬 Technical Specifications

### Layer 1 Details

**Model Type**: Linear (ElasticNet)  
**Frequency**: Monthly  
**Features**: 27 selected from 112 candidates  
**Data Sources**: FRED (US), ECB (EA), Yahoo (FX)  
**Training**: 2014-07 to 2024-12 (126 months)  
**Testing**: 2025-01 to 2025-09 (9 months)  

**Inputs**:
- Rate differentials (1Y, 10Y, real rates)
- Yield curves (US 10Y-3M, EA 10Y-1Y)
- Credit spreads (US HY/BBB, EA HY)
- Inflation (YoY: US CPI, EA HICP)
- Volatility (VIX, VXEEM)
- Liquidity (Fed RRP)
- Labor (US unemployment)

**Outputs**:
- Monthly fair value
- Mispricing (spot - FV)
- Mispricing z-score
- Regime label (In-line / Stretch / Break)

### Layer 2 Details

**Model Type**: Non-linear (XGBoost Trees)  
**Frequency**: Weekly  
**Features**: ~180 engineered features  
**Data Sources**: FRED (US), ECB (EA), Layer 1 (context)  
**Training**: 2014-07 to 2024-12 (~530 weeks)  
**Testing**: 2025-01 to 2025-11 (11 weeks)  

**Inputs**:
- All Layer 1 inputs (weekly frequency)
- FX momentum (1w, 4w, 12w returns)
- Moving averages (4w, 12w, 26w)
- MA crossovers (trend signals)
- FX volatility (4-week rolling)
- Layer 1 context (current z-score, regime)

**Outputs**:
- Predicted Δz (weekly change in mispricing)
- Trading signal (Bullish/Bearish/Neutral)
- Confidence level (High/Medium/Low)

---

## 💡 Key Design Decisions

### Why Two Layers?
1. **Different frequencies** - Monthly (strategy) + Weekly (tactics)
2. **Different purposes** - WHERE vs WHICH WAY
3. **No mathematical blending** - Layers inform narrative, not combined into single forecast
4. **Complementary** - Simple L1 (interpretable) + Complex L2 (accurate)

### Why ElasticNet for Layer 1?
1. **Generalizes better than Ridge** - R² test = 0.455 vs 0.417
2. **More stable than XGBoost** - Smooth FV evolution
3. **Automatic feature selection** - 27/112 features
4. **Interpretable** - Linear coefficients with economic meaning
5. **Production-ready** - Easy to maintain and explain

### Why XGBoost for Layer 2?
1. **Crushes linear models** - 81.8% vs 54.5% hit rate
2. **Captures non-linearity** - Weekly market dynamics are complex
3. **Handles interactions** - Momentum × volatility × regimes
4. **Performance matters** - 27% hit rate improvement justifies complexity
5. **Excels when stretched** - 85.7% accuracy exactly when needed

---

## 📈 2025 Performance Highlights

### Layer 1: Fair Value Tracking
- January-February: Correctly identified EUR undervaluation (-2.23σ)
- March: Called compression to fair value
- July-September: Identified EUR overvaluation (+1.32σ to +1.52σ)
- Mean |z-score|: 1.19σ (active year, not boring!)

### Layer 2: Weekly Signals
- **9 out of 11 weeks correct** (81.8%)
- **6 out of 7 stretched weeks correct** (85.7%)
- **Wins**: W1-W2 (caught compression from -2.23σ), W10 (caught reversal from +1.52σ)
- **Misses**: W7, W9 (momentum continuation, not mean reversion)

---

## 🚀 Deployment Checklist

### Prerequisites
- [ ] Python 3.10+ installed
- [ ] Required packages: pandas, numpy, scikit-learn, xgboost, matplotlib
- [ ] FRED API access for data
- [ ] ECB yield curve CSV data

### One-Time Setup
- [ ] Run `python fx_two_layer_master_runner.py` (full pipeline)
- [ ] Verify outputs in `fx_layer1_outputs/` and `fx_layer2_outputs/`
- [ ] Review `fx_two_layer_summary.json`

### Production Integration
- [ ] Load models from `fx_layer*_outputs/all_models.pkl`
- [ ] Set up monthly data refresh (Layer 1)
- [ ] Set up weekly data refresh (Layer 2)
- [ ] Integrate with FX Views dashboard
- [ ] Set up monitoring and alerts

### Retraining Schedule
- **Layer 1**: Monthly (first week of month)
- **Layer 2**: Weekly (every Friday)
- **Full evaluation**: Quarterly

---

## 📞 Support & Questions

### Documentation Issues
- Check README and Quickstart first
- Review white papers for technical details
- Examine CSV files for raw data

### Implementation Help
- See "Technical Implementation" sections in white papers
- Review `fx_models_input_output_summary.json`
- Check existing code in `fx_*.py` files

### Model Questions
- White papers contain full methodology
- Coefficient/importance files show feature effects
- Output folders contain predictions and metadata

---

## 📝 Version History

**v1.0** (Current)
- Layer 1: ElasticNet (α=0.0001, L1_ratio=0.70)
- Layer 2: XGBoost (n_est=200, lr=0.05, depth=3)
- Training: 2014-07 to 2024-12
- Test: 2025-01 to 2025-09 (L1), 2025-01 to 2025-11 (L2)

---

## 🎯 Next Steps

1. **Read the white papers** - Start with Layer 1, then Layer 2
2. **Examine the data** - Open CSV files in Excel/Python
3. **Review visualizations** - Look at charts and diagrams
4. **Run the models** - Use Quickstart guide
5. **Integrate into dashboard** - Follow implementation sections

---

## 📄 File Manifest

### Documentation (Markdown)
- FX_TWO_LAYER_FRAMEWORK_INDEX.md (this file)
- FX_LAYER1_WHITE_PAPER.md
- FX_LAYER2_WHITE_PAPER.md
- README_FX_TWO_LAYER_FRAMEWORK.md
- FX_TWO_LAYER_QUICKSTART.md

### Data Files (CSV)
- fx_layer1_elasticnet_coefficients_full.csv
- fx_layer1_all_models_comparison.csv
- fx_layer2_xgboost_importances_full.csv
- fx_layer2_all_models_comparison.csv

### Configuration (JSON)
- fx_models_input_output_summary.json
- fx_two_layer_summary.json
- fx_layer1_outputs/layer1_recommendation.json
- fx_layer2_outputs/layer2_recommendation.json

### Visualizations (PNG)
- fx_2025_spot_vs_predicted.png
- fx_two_layer_framework_diagram.png

### Model Artifacts (PKL)
- fx_layer1_outputs/all_models.pkl
- fx_layer2_outputs/all_models.pkl

### Analysis (TXT)
- fx_layer2_summary_table.txt

---

**Framework Version**: 1.0  
**Documentation Date**: 2025  
**Total Pages**: 80+ pages of technical documentation  
**Status**: Production Ready ✅  

---

*End of Index*


