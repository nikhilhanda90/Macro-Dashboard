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

## 🚀 Deployment & Updates

### Initial Setup (One Time)
1. **Push to GitHub:** `git add . && git commit -m "Initial" && git push`
2. **Deploy on Streamlit Cloud:** https://share.streamlit.io (connect repo)
3. **Add Secret:** `FRED_API_KEY = "your_key"` in Streamlit settings
4. **Deploy!** Dashboard goes live in 2-3 minutes

### Weekly Maintenance (Every Tuesday)
1. **Run:** Double-click `WEEKLY_UPDATE.bat` (generates FX Views)
2. **Push:** `git add FX Views/*outputs/* && git commit -m "Update FX" && git push`
3. **Done!** Streamlit auto-deploys in 1-2 minutes

📖 **Full Guide:** See `/DEPLOYMENT_CHECKLIST.md` in project root

---

## 🎯 Quick Reference

### What Updates Automatically?
✅ US Macro (23 indicators) - FRED API (real-time)  
✅ EU Macro (9 indicators) - FRED API (real-time)  
✅ Technicals - Yahoo Finance (daily)  
✅ CFTC Positioning - CFTC website (weekly auto-fetch)

### What Needs Weekly Push?
⚠️ FX Valuation Charts - Model outputs (run `WEEKLY_UPDATE.bat` → push)  
⚠️ 8 Eurozone CSVs - Manual update (monthly)

### Cache Settings
- **Macro indicators:** 1 hour (Streamlit cache)
- **FX Views:** Static files (update via push)
- **Manual refresh:** Browser Ctrl+F5

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

