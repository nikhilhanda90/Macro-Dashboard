# FX Views Update Workflow

## 📊 Two-Tier Update System

### **🔄 WEEKLY UPDATE** (Every Tuesday after market close)
**File**: `WEEKLY_UPDATE.bat`

**What it does:**
1. ✅ **Retrains Layer 2 (Pressure Model)** with latest weekly data
   - Model: LightGBM binary classifier (locked architecture)
   - Adds new week of rates, credit, vol, liquidity, FX momentum data
   - Regenerates `lightgbm_binary_predictions.csv`
2. ✅ **Regenerates charts** using latest Layer 1 + Layer 2 predictions
3. ✅ **Updates technicals** from Yahoo Finance (real-time)
4. ✅ **Fetches CFTC positioning** (weekly release)
5. ✅ **Regenerates decision summary** with assertive Nikhil-style text

**When to run:** Every Tuesday after market close

**What gets updated:**
- Layer 2 predictions (fresh weekly pressure signals)
- Charts (using latest Layer 1 + updated Layer 2)
- Technicals (real-time from Yahoo)
- Positioning (latest CFTC release)
- Decision text (synthesizes all 4 layers)

**What stays the same:**
- Layer 1 predictions (macro fair value — acceptable to be 1-4 weeks stale)

---

### **📅 MONTHLY UPDATE** (When new macro data arrives)
**File**: `MONTHLY_UPDATE.bat`

**What it does:**
1. ✅ **Retrains Layer 1 (Valuation Model)** with latest macro data
   - Model: ElasticNet (locked architecture)
   - Adds new month of US/Eurozone macro indicators
   - Regenerates `elasticnet_predictions.csv`
2. ✅ **Then runs WEEKLY_UPDATE.bat** (Layer 2, charts, etc.)

**When to run:** Once a month when fresh macro data is published (e.g. CPI, jobs, PMIs, etc.)

**What gets updated:**
- Layer 1 predictions (macro fair value with latest fundamentals)
- Everything in weekly update (Layer 2, charts, technicals, positioning)

---

## 🔒 Model Architecture (Locked)

| Layer | Model | Training Data | Update Frequency |
|-------|-------|---------------|------------------|
| **Layer 1** | ElasticNet | Monthly macro indicators | Monthly |
| **Layer 2** | LightGBM Binary | Weekly rates/credit/vol/FX | Weekly |
| **Layer 3** | Rules-based technical indicators | Daily Yahoo Finance | Weekly |
| **Layer 4** | CFTC positioning | Weekly CFTC release | Weekly |

**"Training" = Retraining with latest data, NOT changing model architecture!**

---

## 🚀 Usage

### Weekly (Every Tuesday):
```bash
cd "C:\Users\NikhilHanda\Documents\Macro-Dashboard"
WEEKLY_UPDATE.bat
```
Then commit and push:
```bash
git add FX Views/3_layer2_models/fx_layer2_outputs/*
git add FX Views/5_outputs/*
git add FX Views/technical_outputs/*
git add FX Views/cftc_outputs/*
git commit -m "Weekly FX Views update - [DATE]"
git push origin main
```

### Monthly (When macro data arrives):
```bash
cd "C:\Users\NikhilHanda\Documents\Macro-Dashboard"
MONTHLY_UPDATE.bat
```
Then commit and push:
```bash
git add FX Views/2_layer1_models/fx_layer1_outputs/*
git add FX Views/3_layer2_models/fx_layer2_outputs/*
git add FX Views/5_outputs/*
git add FX Views/technical_outputs/*
git add FX Views/cftc_outputs/*
git commit -m "Monthly FX Views update - Layer 1 retrained with [MONTH] data"
git push origin main
```

---

## ⏱️ Data Freshness

| Component | Update Mechanism | Staleness |
|-----------|------------------|-----------|
| **Layer 1 (Valuation)** | Monthly retrain | 0-4 weeks stale (acceptable) |
| **Layer 2 (Pressure)** | Weekly retrain | 0-7 days stale |
| **Technicals** | Yahoo Finance API | Real-time (cached 1hr in Streamlit) |
| **Positioning** | CFTC weekly fetch | 0-7 days stale |
| **Decision text** | Generated on update | Fresh with latest data |

---

## 📁 What Gets Committed to GitHub

**Weekly:**
- `FX Views/3_layer2_models/fx_layer2_outputs/*` (Layer 2 predictions)
- `FX Views/5_outputs/*` (charts + decision JSON)
- `FX Views/technical_outputs/*` (technicals)
- `FX Views/cftc_outputs/*` (positioning)

**Monthly:**
- `FX Views/2_layer1_models/fx_layer1_outputs/*` (Layer 1 predictions)
- All weekly updates

---

## ✅ Streamlit Cloud Auto-Deploy

After you push to GitHub:
- Streamlit Cloud detects the commit
- Auto-deploys in 1-2 minutes
- Users see fresh data immediately

**No manual Streamlit refresh needed!** 🚀

