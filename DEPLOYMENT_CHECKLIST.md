# 🚀 Streamlit Cloud Deployment Checklist

## ✅ One-Time Setup

### 1. GitHub Repository
- [ ] Create repo: `nikhil-macro-dashboard` (or your preferred name)
- [ ] Push all code from `C:\Users\NikhilHanda\Documents\Macro-Dashboard`
- [ ] Verify `.gitignore` excludes secrets

### 2. Streamlit Cloud Setup
- [ ] Go to https://share.streamlit.io
- [ ] Sign in with GitHub
- [ ] Click "New app"
- [ ] Select your repo
- [ ] Main file: `Regional_Macro_Insights.py`
- [ ] Click "Advanced settings"

### 3. Add Secrets (CRITICAL!)
In Streamlit Cloud Advanced Settings → Secrets:

```toml
FRED_API_KEY = "your_actual_fred_api_key_here"
```

### 4. Deploy!
- [ ] Click "Deploy"
- [ ] Wait 2-3 minutes
- [ ] Your dashboard will be live at: `https://share.streamlit.io/[username]/[repo]/Regional_Macro_Insights.py`

---

## 🔄 Weekly Maintenance (Option 1)

**Every Tuesday after market close** (CFTC releases new data):

### Step 1: Update FX Views Locally
```bash
cd "C:\Users\NikhilHanda\FX Views"
py generate_fx_views_complete.py
```

This generates:
- 4 updated charts (PNG files)
- New decision JSON
- Updated technical summary
- Latest CFTC positioning

### Step 2: Copy to Dashboard Folder
```bash
# Already automated - files go to correct location
xcopy "C:\Users\NikhilHanda\FX Views\5_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\5_outputs\" /Y
xcopy "C:\Users\NikhilHanda\FX Views\technical_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\technical_outputs\" /Y
xcopy "C:\Users\NikhilHanda\FX Views\cftc_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\cftc_outputs\" /Y
```

### Step 3: Commit & Push to GitHub
```bash
cd "C:\Users\NikhilHanda\Documents\Macro-Dashboard"
git add FX Views/5_outputs/*
git add FX Views/technical_outputs/*
git add FX Views/cftc_outputs/*
git commit -m "Update FX Views - Week of [DATE]"
git push origin main
```

### Step 4: Verify Update
- Streamlit Cloud auto-deploys (takes 1-2 minutes)
- Visit your dashboard URL
- Refresh page (Ctrl+F5)
- Check "Last Updated" timestamp in FX Views

---

## 🔧 What Updates Automatically (No Work Needed)

### Always Fresh (Every Page Load):
- ✅ **US Macro Indicators** (23 indicators from FRED API)
- ✅ **Eurozone Macro** (9 indicators from FRED API)
- ✅ **Technical Analysis** (Daily price data from Yahoo Finance)
- ✅ **CFTC Positioning** (Weekly data from CFTC website)

### Needs Weekly Push (Tuesday):
- ❌ **FX Valuation Charts** (Layer 1 + Layer 2 model outputs)
- ❌ **FX Decision Summary** (Synthesis JSON)

---

## 📊 What Users See

**After Each Weekly Update:**
- New FX Views charts reflecting latest macro data
- Updated pressure signals (binary expand/compress)
- Fresh technical analysis
- Latest CFTC positioning

**Between Updates (Automatic):**
- US/Eurozone macro dashboards stay current
- Technical indicators refresh daily
- Everything except FX model outputs

---

## 🐛 Troubleshooting

**If FX Views shows errors:**
1. Check that output files exist in GitHub repo
2. Verify paths in `pages/1_💱_FX_Insights.py`
3. Check Streamlit Cloud logs

**If macro data is stale:**
1. Check FRED API key in secrets
2. Verify indicator series IDs are correct
3. Check FRED rate limits (120 requests/min)

**If deployment fails:**
1. Check `requirements.txt` has all dependencies
2. Verify Python version compatibility (3.8+)
3. Check Streamlit Cloud build logs

---

## 📅 Recommended Schedule

**Weekly (Tuesday 5pm):**
- Run FX Views update script
- Push to GitHub
- Verify deployment

**Monthly (First Monday):**
- Check for stale Eurozone CSVs
- Update if needed
- Review dashboard performance

**Quarterly:**
- Review model performance
- Update documentation
- Check for new FRED series

---

## 🎯 Success Metrics

Your dashboard is working correctly when:
- ✅ All US indicators show recent dates
- ✅ Eurozone indicators show recent dates
- ✅ FX Views decision summary has current week
- ✅ Charts display without errors
- ✅ No "data not available" warnings

---

## 🔮 Future: Full Automation (Option 2)

When ready, set up **GitHub Actions** to eliminate weekly manual work:
- Auto-run FX Views generation
- Auto-commit and push
- Fully hands-off

(See separate GitHub Actions workflow guide)

---

**Questions? Check:**
- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- FRED API Docs: https://fred.stlouisfed.org/docs/api/
- Dashboard README: `README.md`

