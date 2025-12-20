# FX Two-Layer Framework - Deployment Strategy

## Current State
- **Layer 1**: ElasticNet model (monthly fair value)
- **Layer 2**: XGBoost model (weekly pressure signal)
- **Dashboard**: Streamlit (ready for Streamlit Cloud)

---

## Deployment Options Analysis

### Option 1: Streamlit Cloud (Recommended for V1) ⭐
**How it works**:
- Deploy Streamlit app to cloud (free tier available)
- App loads pre-trained models (pickle files)
- Fetches fresh data on each page load (with caching)
- User visits page → triggers data refresh → shows latest view

**Pros**:
✅ Simple - matches your existing dashboard setup  
✅ Free (Streamlit Community Cloud)  
✅ No infrastructure management  
✅ Automatic scaling  
✅ Users always see latest data (on-demand refresh)  
✅ You already have Streamlit experience

**Cons**:
⚠️ Data fetched on page load (adds 10-20 sec load time first visit)  
⚠️ Models stay static (need manual retrain + redeploy to update)  
⚠️ Limited compute (1 GB RAM on free tier)

**Best for**: V1 MVP deployment

---

### Option 2: GitHub Actions + Streamlit Cloud (Recommended for V2) 🚀
**How it works**:
```
Daily 6 AM ET (GitHub Actions):
  ↓
1. Fetch latest data (FRED API)
  ↓
2. Update Layer 1 fair value (uses trained model)
  ↓
3. Update Layer 2 pressure signal (uses trained model)
  ↓
4. Save results to CSV/JSON
  ↓
5. Commit & push to repo
  ↓
Streamlit app reads pre-computed results (instant load)
```

**Pros**:
✅ Fully automated daily updates  
✅ Fast page loads (reads pre-computed files)  
✅ Free (GitHub Actions = 2000 min/month)  
✅ Version control for predictions  
✅ Audit trail of historical predictions  
✅ Can run model retraining monthly  

**Cons**:
⚠️ Requires GitHub Actions setup (20 min one-time config)  
⚠️ 24-hour minimum refresh (not real-time)

**Best for**: V2 production deployment

---

### Option 3: AWS Lambda / Cloud Functions (Overkill for Now)
**How it works**:
- Serverless functions triggered by schedule
- Runs Python model in cloud
- Stores results in S3/Cloud Storage
- Dashboard reads from storage

**Pros**:
✅ Scalable  
✅ Real-time capable  
✅ Professional-grade

**Cons**:
❌ Complex setup  
❌ Costs money  
❌ Overkill for FX models  
❌ More moving parts to maintain

**Best for**: Enterprise deployment (not needed now)

---

### Option 4: Local Cron Job (Not Recommended)
**How it works**:
- Script runs on your local machine daily
- Pushes results to cloud storage
- Dashboard reads from storage

**Pros**:
✅ Simple to test locally

**Cons**:
❌ Computer must be on 24/7  
❌ Not reliable for production  
❌ Manual intervention if it breaks

**Best for**: Development/testing only

---

## Recommended Path: Phased Deployment

### Phase 1: V1 MVP (This Week) - Streamlit Cloud
**What to deploy**:
```python
# FX Views Dashboard (Streamlit)
1. Load pre-trained models (elasticnet.pkl, xgboost.pkl)
2. On page load:
   - Fetch latest data (yfinance + FRED, cached 1 hour)
   - Run Layer 1 → Monthly FV + regime
   - Run Layer 2 → Weekly pressure signal
   - Generate AI narrative (Nikhil style)
3. Display unified FX view
```

**Refresh cadence**:
- First visitor each hour triggers data refresh
- Cached for 1 hour (fast for subsequent users)
- Models stay static (retrain offline quarterly)

**Deployment steps**:
1. Create `fx_views_dashboard.py` (Streamlit app)
2. Add `requirements.txt` (dependencies)
3. Push to GitHub
4. Deploy to Streamlit Cloud (1 click)
5. Done! ✅

**Estimated time**: 2-3 hours to build + deploy

---

### Phase 2: V2 Production (Next Month) - GitHub Actions + Streamlit

**What to automate**:
```yaml
# .github/workflows/fx_daily_update.yml
Daily at 6:00 AM ET:
  1. Fetch data (FRED + yfinance)
  2. Run Layer 1 model → Save fx_layer1_latest.json
  3. Run Layer 2 model → Save fx_layer2_latest.json
  4. Generate historical predictions log
  5. Commit results to repo
  
Monthly (1st of month):
  1. Retrain Layer 1 model with new data
  2. Update model pickle if performance improved
  3. Alert via email if model drift detected
  
Weekly (Monday):
  1. Generate weekly FX report (PDF)
  2. Archive predictions for backtesting
```

**Dashboard reads**:
- Pre-computed results (instant load)
- Historical prediction accuracy chart
- Model performance tracker

**Estimated time**: 4-5 hours to set up GitHub Actions

---

## My Recommendation: Start with Option 1, Upgrade to Option 2

### **For Now (V1 MVP)**:
✅ Deploy to **Streamlit Cloud** with on-demand data refresh  
✅ Keep models static (retrain manually quarterly)  
✅ Simple, fast, reliable  
✅ Gets your framework live in production TODAY

### **After Testing (V2 Production)**:
🚀 Add **GitHub Actions** for daily automation  
🚀 Pre-compute predictions (faster load)  
🚀 Version control predictions (audit trail)  
🚀 Automated monthly retraining

---

## Data Refresh Strategy

### Layer 1 (Monthly Model)
**When to update**: 
- End of each month (after macro data releases)
- Monthly data releases lag by 2-4 weeks
- Run on the 15th of each month (safe delay)

**How to update**:
```python
# Monthly job
1. Fetch latest monthly macro (FRED)
2. Load trained ElasticNet model
3. Predict fair value for latest month
4. Calculate z-score & regime
5. Save to fx_layer1_latest.json
```

### Layer 2 (Weekly Model)
**When to update**:
- Every Monday morning (after Friday close)
- Uses previous week's market data

**How to update**:
```python
# Weekly job (Monday 6 AM)
1. Fetch latest weekly market data (yields, spreads, VIX)
2. Load trained XGBoost model
3. Predict weekly pressure signal
4. Calculate hit rate vs actual (if available)
5. Save to fx_layer2_latest.json
```

### Daily Data Refresh (For Dashboard Display)
**What refreshes daily**:
- Current EURUSD spot price
- Today's US/EA yields
- Today's credit spreads
- Today's VIX

**Used for**:
- "As of [today]" display
- Latest z-score calculation
- Current regime status

---

## Cost Analysis

| Option | Setup Time | Monthly Cost | Complexity |
|--------|------------|--------------|------------|
| **Streamlit Cloud (V1)** | 2 hours | $0 | Low ⭐ |
| **+ GitHub Actions (V2)** | +4 hours | $0 | Medium ⭐⭐ |
| AWS Lambda | 8 hours | ~$10-20 | High ⭐⭐⭐ |

**Winner**: Streamlit Cloud → GitHub Actions path (free, simple, scalable)

---

## Questions for You

Before I build the integration, please confirm:

1. **Deployment platform**: Start with Streamlit Cloud? ✅
2. **Refresh cadence**: 
   - Daily spot/market data? (1-hour cache)
   - Weekly Layer 2 updates? (manual trigger or wait for GH Actions?)
   - Monthly Layer 1 updates? (manual trigger?)
3. **Model retraining**: 
   - Manual quarterly? (you decide when)
   - Or automated monthly? (needs GH Actions)
4. **Where in your site**: 
   - FX Views page (existing)?
   - New dedicated "FX Model" page?
   - Integrated into Stratiri website (stratiri-website)?

---

## Next Steps (Once You Confirm)

1. ✅ Build `fx_views_streamlit.py` (Streamlit dashboard)
2. ✅ Create data refresh module (fetch_latest_data.py)
3. ✅ Integrate Layer 1 + Layer 2 predictions
4. ✅ Generate AI narrative (Nikhil macro voice)
5. ✅ Deploy to Streamlit Cloud
6. ✅ Test live
7. 🎯 Move to Layer 3 (technical indicators)

---

**Your turn**: What deployment approach do you prefer? I'm ready to build once we align! 🚀

---

**Document Created**: December 2025  
**Status**: Awaiting deployment decision


