# 🌍 Nikhil Macro Dashboard

**Regional Macro Analysis + FX Views | US, Eurozone, EURUSD**

Live dashboard for macro cycle tracking and FX decision-making.

---

## 📊 What's Inside

### 🌍 **Macro View** (Main Page)
- **US**: 23 leading/coincident/lagging indicators
- **Eurozone**: 17 indicators (FRED + CSV data)
- **Compare Mode**: Nikhil Macro Score (US vs EU divergence)

### 💱 **FX Views** (EURUSD)
**Decision-first framework with 4 layers:**
1. **Valuation & Pressure** (4-chart grid)
   - Macro Fair Value vs Spot
   - Mispricing Z-Score
   - Weekly Pressure (Binary: Expand/Compress)
   - Decision Map (Quadrants)
2. **Technicals** (Execution context)
3. **Positioning** (CFTC asymmetry signals)

---

## 🚀 Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run Regional_Macro_Insights.py
```

Dashboard opens at: **http://localhost:8501**

---

## ☁️ Deploy to Streamlit Cloud

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/[username]/[repo].git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Connect GitHub repo
3. Main file: `dashboard_regional.py`
4. Add secret: `FRED_API_KEY = "your_key"`
5. Deploy!

---

## 🔄 Weekly Maintenance

### Update FX Views (Every Tuesday)

**Option 1: Use Batch File (Windows)**
```bash
# Double-click:
WEEKLY_UPDATE.bat

# Then commit:
git add FX Views/5_outputs/* FX Views/technical_outputs/* FX Views/cftc_outputs/*
git commit -m "Update FX Views"
git push
```

**Option 2: Manual**
```bash
cd "FX Views"
py generate_fx_views_complete.py
# Copy outputs to dashboard folder
# Commit and push
```

**What Updates Automatically:**
- ✅ US macro (FRED API)
- ✅ Eurozone macro (FRED API)
- ✅ Technicals (Yahoo Finance)
- ✅ CFTC positioning (weekly)

**What Needs Weekly Push:**
- ❌ FX Valuation charts (model outputs)

---

## 📁 Project Structure

```
Macro-Dashboard/
├── Regional_Macro_Insights.py     # Main Streamlit app
├── pages/
│   └── 1_💱_FX_Insights.py       # FX Views page
├── FX Views/
│   ├── 1_data_pipeline/          # Data fetchers
│   ├── 2_layer1_models/          # Valuation models
│   ├── 3_layer2_models/          # Pressure models
│   ├── 4_visualization/          # Chart generation
│   ├── 5_outputs/                # Generated charts/JSON
│   ├── technical_outputs/        # Technical analysis
│   └── cftc_outputs/             # Positioning data
├── eurozone_data/                # CSV files (8 indicators)
├── requirements.txt              # Dependencies
└── DEPLOYMENT_CHECKLIST.md       # Full deployment guide
```

---

## 🔑 Required Secrets

**Streamlit Cloud (`.streamlit/secrets.toml`):**
```toml
FRED_API_KEY = "your_fred_api_key"
```

Get your FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

---

## 🎯 Features

### Macro View
- ✅ Leading/Coincident/Lagging framework
- ✅ Z-score normalization (All-time + 5Y)
- ✅ Momentum detection
- ✅ Auto-generated commentary (Nikhil voice)
- ✅ Category aggregation (Fixed Income, Labor, Inflation, etc.)

### FX Views
- ✅ 2-Layer framework (Valuation + Pressure)
- ✅ Binary pressure signals (Expand/Compress)
- ✅ Decision matrix (4 layers synthesized)
- ✅ Chart explainers (Purpose + How to Read + Right Now)
- ✅ Collapsible sections
- ✅ NO Δz predictions surfaced (only binary)

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data**: FRED API, Yahoo Finance, CFTC, Eurostat
- **ML**: scikit-learn (ElasticNet), LightGBM
- **Viz**: Plotly, Matplotlib
- **Deployment**: Streamlit Cloud + GitHub

---

## 📚 Documentation

- **Deployment**: See `DEPLOYMENT_CHECKLIST.md`
- **FX Views Architecture**: See `FX Views/FX_VIEWS_COMPLETE_GUIDE.md`
- **Weekly Updates**: See `WEEKLY_UPDATE.bat`

---

## 🔮 Roadmap

**V1 (Current):**
- ✅ Regional macro dashboard
- ✅ FX Views (EURUSD)
- ✅ Binary pressure framework
- ✅ Manual weekly updates

**V2 (Future):**
- [ ] GitHub Actions (full automation)
- [ ] AI-generated commentary (replace rules-based)
- [ ] Multi-pair support (GBPUSD, USDJPY)
- [ ] Real-time data refresh
- [ ] User overrides for extreme scenarios

---

## 📧 Support

Questions? Check:
- Streamlit Docs: https://docs.streamlit.io
- FRED API: https://fred.stlouisfed.org/docs/api/
- Issues: (your GitHub issues page)

---

**Built by Nikhil | Updated: 2025-12-26**

