# 📚 Macro View Dashboard - Education & Documentation

**Welcome to the knowledge base for the Macro View Dashboard.**

This folder contains detailed documentation on data sources, methodologies, and operational procedures.

---

## 📂 Documentation Files

### [DATA_SOURCES_AND_REFRESH.md](./DATA_SOURCES_AND_REFRESH.md)
**Complete data inventory and refresh schedule**

Learn about:
- Every indicator in US and Eurozone dashboards (names, sources, frequencies)
- How EUR/USD technical analysis works
- How FX valuation models operate
- CFTC positioning data
- What updates automatically vs. manually
- Maintenance schedule and troubleshooting

**👉 START HERE if you're new or need to understand data operations**

---

## 🎯 Quick Reference

### What Updates Automatically?
✅ US Macro (23 indicators) - Daily via FRED API  
✅ EU Macro (14 indicators) - Daily via FRED API  
✅ EUR/USD Technicals - Hourly via Yahoo Finance  

### What Requires Manual Updates?
⚠️ 9 Eurozone CSV indicators - Monthly  
⚠️ FX Valuation models - Quarterly (retrain + regenerate)  
⚠️ CFTC Positioning - Weekly (pending auto-implementation)  

### Cache Settings
- **Macro indicators:** 24 hours
- **EUR/USD technicals:** 1 hour
- **Manual refresh:** "Clear Cache" button in sidebar

---

## 🔗 External Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **Eurostat Help:** https://ec.europa.eu/eurostat/help/support
- **CFTC Data:** https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
- **yfinance (Yahoo Finance):** https://pypi.org/project/yfinance/

---

## 📧 Support

For questions about data sources or methodology:
- **Data Issues:** Check DATA_SOURCES_AND_REFRESH.md troubleshooting section
- **Model Questions:** See FX Views white papers in `/FX Views/white_papers/`
- **Technical Support:** Contact dashboard administrator

---

**Last Updated:** December 22, 2024  
**Version:** 1.0

