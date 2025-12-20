# FX Two-Layer Framework - V2 Roadmap

## V1 Status: ✅ Complete & Production Ready
- **Layer 1**: ElasticNet (R² = 0.455, stable monthly fair value)
- **Layer 2**: XGBoost (90.9% hit rate on weekly pressure signals)
- **White Paper**: Complete documentation
- **Ready for deployment**: Yes

---

## V2 Enhancements (Future)

### 1. Layer 2: Add LightGBM Model
**Status**: Deferred due to Python 3.14 compatibility issues

**Issue**: 
- LightGBM 4.6.0 installed successfully
- Standalone import works
- Full training fails due to scipy/sklearn bytecode compilation issues with Python 3.14
- Multiple workarounds attempted (PYTHONDONTWRITEBYTECODE, background jobs, ASCII-only output)

**Solution for V2**:
- Wait for Python 3.14 + scipy stability updates
- OR downgrade to Python 3.11/3.12 for compatibility
- OR test in isolated virtual environment

**Expected Impact**: 
- LightGBM typically performs similarly to XGBoost
- Would provide 4th model for ensemble validation
- Not critical given XGBoost's 90.9% performance

**Priority**: Low (nice-to-have, not blocking)

---

### 2. Other V2 Considerations

#### Layer 1 Enhancements
- [ ] Add regime-specific models (Bull/Bear/Neutral)
- [ ] Include ECB/Fed policy divergence indicators
- [ ] Test quarterly retraining cadence

#### Layer 2 Enhancements
- [ ] Add LightGBM (pending Python compatibility)
- [ ] Test ensemble of top 2-3 models
- [ ] Add confidence intervals on predictions
- [ ] Weekly automated retraining

#### Infrastructure
- [ ] Automated daily data refresh
- [ ] Model monitoring dashboard
- [ ] Performance tracking vs actuals
- [ ] Drift detection alerts

#### Dashboard Integration
- [ ] Embed Layer 1 + Layer 2 signals into FX Views page
- [ ] Add interactive regime chart
- [ ] Show top 5 feature importances dynamically
- [ ] Historical prediction accuracy chart

---

## Version History

### V1.0 (December 2025)
- Initial two-layer framework
- 5 Layer 1 models tested → ElasticNet selected
- 3 Layer 2 models tested → XGBoost selected
- Full white paper documentation
- 2014-2025 backtest complete

### V2.0 (Planned - Q1 2026)
- LightGBM integration (pending Python fix)
- Dashboard deployment
- Automated data pipeline
- Performance monitoring

---

**Document Created**: December 2025  
**Last Updated**: December 2025


