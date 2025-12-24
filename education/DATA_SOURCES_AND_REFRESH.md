# Macro View Dashboard - Data Sources & Refresh Schedule

**Last Updated:** December 24, 2024  
**Production Version:** 1.2

---

## 📊 US MACRO INDICATORS

### Data Source
- **Primary:** FRED (Federal Reserve Economic Data) API
- **Refresh:** Auto-fetches daily (cache expires every 24 hours)
- **First load after cache expiry:** ~10-15 seconds
- **Subsequent loads:** Instant (cached)

### Leading Indicators (14)
| Indicator | Series ID | Frequency | Description |
|-----------|-----------|-----------|-------------|
| 10Y Real Rate (TIPS) | DFII10 | Daily | Real cost of capital |
| US Yield Curve (10Y-2Y) | T10Y2Y | Daily | Recession indicator |
| Credit Spreads (IG) | BAMLC0A4CBBB | Daily | Corporate stress gauge |
| Credit Spreads (HY) | BAMLH0A0HYM2 | Daily | Junk bond risk premium |
| S&P 500 | ^GSPC | Daily | Equity market sentiment |
| VIX | ^VIX | Daily | Fear gauge |
| ISM Manufacturing PMI | NAPM | Monthly | Factory sentiment |
| ISM New Orders | NAPMNOI | Monthly | Future demand signal |
| Building Permits | PERMIT | Monthly | Housing starts proxy |
| Initial Claims (4W MA) | ICSA | Weekly | Labor market health |
| Consumer Confidence | UMCSENT | Monthly | Household optimism |
| Leading Economic Index | USSLIND | Monthly | Composite forward signal |
| Fed Funds Rate | DFF | Daily | Monetary policy stance |
| M2 Money Supply (YoY) | M2SL | Monthly | Liquidity conditions |

### Coincident Indicators (5)
| Indicator | Series ID | Frequency | Description |
|-----------|-----------|-----------|-------------|
| Unemployment Rate | UNRATE | Monthly | Labor slack |
| Nonfarm Payrolls | PAYEMS | Monthly | Job creation |
| Industrial Production | INDPRO | Monthly | Factory output |
| Retail Sales | RSXFS | Monthly | Consumer spending |
| Real GDP (QoQ SAAR) | A191RL1Q225SBEA | Quarterly | Economic growth |

### Lagging Indicators (4)
| Indicator | Series ID | Frequency | Description |
|-----------|-----------|-----------|-------------|
| Core CPI (YoY) | CPILFESL | Monthly | Inflation ex food/energy |
| Average Hourly Earnings (YoY) | CES0500000003 | Monthly | Wage growth |
| Consumer Credit (YoY) | TOTALSL | Monthly | Household leverage |
| Fed Funds Rate | DFF | Daily | Policy rate (confirms cycle) |

---

## 🇪🇺 EUROZONE MACRO INDICATORS

### Mixed Data Sources

#### FRED API (Auto-fetch daily)
| Indicator | Series ID | Frequency | Description |
|-----------|-----------|-----------|-------------|
| Euro 1Y Yield | IRSTCI01EZM156N | Monthly | Short-term rates |
| Euro 10Y Yield | IRLTLT01EZM156N | Monthly | Long-term rates |
| German 10Y Bund | IRLTLT01DEM156N | Monthly | Safe haven benchmark |
| French 10Y OAT | IRLTLT01FRM156N | Monthly | Peripheral risk gauge |
| Euro HY Spread | BAMLHE00EHYIEY | Daily | Credit stress |
| Real GDP | CLVMNACSCAB1GQEA19 | Quarterly | Growth |
| EM Vol Index | VXEEMCLS | Daily | Risk proxy |
| Core HICP | CP0000EZ19M086NEST | Monthly | Inflation |
| ECB Deposit Rate | ECBDFR | Irregular | Policy rate |

#### Static CSV Files (Manual monthly update)
**Location:** `eurozone_data/` folder  
**Last Updated:** December 20, 2024  
**Update Frequency:** Manual (monthly recommended)

| Indicator | CSV File | Frequency | Description |
|-----------|----------|-----------|-------------|
| Economic Sentiment Index | eurostat_industrial_confidence_ea20.csv | Monthly | Business confidence |
| Consumer Confidence | eurostat_industrial_confidence_ea20.csv | Monthly | Household sentiment |
| Unemployment Rate | eurostat_unemployment_ea20.csv | Monthly | Labor slack |
| Employment Rate | eurostat_employment_ea20.csv | Quarterly | Employment ratio |
| Retail Sales Volume | eurostat_retail_ea20.csv | Monthly | Consumer spending |
| House Prices | eurostat_house_prices_ea20.csv | Quarterly | Property market |
| Labor Cost Index | eurostat_ulc_ea20.csv | Quarterly | Wage pressure |
| HICP Headline | eurostat_hicp_headline_ea20.csv | Monthly | Headline inflation |
| Industrial Confidence | eurostat_industrial_confidence_ea20.csv | Monthly | Manufacturing sentiment |

**⚠️ ACTION REQUIRED:** Update these 9 CSV files monthly from [Eurostat](https://ec.europa.eu/eurostat/data/database)

---

## 💱 FX INSIGHTS - EURUSD

### 1️⃣ Technical Analysis

**Data Source:** Yahoo Finance (yfinance library)  
**Refresh:** Auto-generates every 1 hour  
**Data Window:** 2 years of daily OHLC  

**Indicators Calculated:**
- Price: Daily Open, High, Low, Close
- Moving Averages: 50d, 100d, 200d SMA
- RSI (14-day)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2)
- ATR (20-day)
- 1-year High/Low

**Outputs:**
- Technical Bias Score (-3 to +3)
- Trade Posture (Buy Breakouts, Fade Rallies, etc.)
- Structure/Momentum components
- Key level triggers

**Cache Behavior:**
- First visitor after 1 hour: Fetches fresh data (~20 seconds)
- Other visitors: Instant (uses cached analysis)
- Manual refresh: Clear cache button in sidebar

---

### 2️⃣ Valuation Models (Layer 1 & 2)

**Status:** ⚠️ STATIC (Manual retraining required)

**Layer 1 - Monthly Macro Valuation**
- **Model:** ElasticNet (trained on macro fundamentals)
- **Inputs:** US vs EA yields, inflation, credit spreads, liquidity
- **Output:** Fair Value, Mispricing Z-score, Regime label
- **Training Data:** 2010-2024
- **Predictions:** Pre-generated through Dec 2025
- **Refresh Frequency:** Manual (quarterly recommended)

**Layer 2 - Weekly Pressure Signal**
- **Model:** XGBoost (trained on flow/momentum)
- **Inputs:** Market yields, credit spreads, VIX, RRP, FX momentum
- **Output:** Pressure direction (compress/expand)
- **Training Data:** 2010-2024
- **Predictions:** Pre-generated through Dec 2025
- **Refresh Frequency:** Manual (quarterly recommended)

**⚠️ PRODUCTION NOTE:**  
Valuation models require Python script execution to retrain/update predictions.  
Current implementation uses static CSV files generated on Dec 20, 2024.

**Files:**
- `FX Views/2_layer1_models/fx_layer1_outputs/*.csv` (Fair value predictions)
- `FX Views/3_layer2_models/fx_layer2_outputs/*.csv` (Pressure predictions)
- `FX Views/5_outputs/*.json` (Decision table)

---

### 3️⃣ CFTC Positioning

**Status:** ⚠️ STATIC (Manual update required)

**Data Source:** CFTC Commitments of Traders (COT) Report  
**Asset:** EUR FX Futures  
**Trader Group:** Non-Commercial (speculative)  
**Report Frequency:** Weekly (released Friday, data as of Tuesday)  
**Current Implementation:** Static sample data (Dec 20, 2024)

**Metrics:**
- Net Position (long - short contracts)
- Z-Score (6-month and 1-year windows)
- Historical Percentile
- Positioning State (Crowded Long/Short/Neutral)

**⚠️ ACTION REQUIRED:** Implement auto-fetch from CFTC API

**Files:**
- `FX Views/cftc_outputs/cftc_eur_positioning.csv` (Historical data)
- `FX Views/cftc_outputs/cftc_positioning_summary.json` (Latest snapshot)

---

## ⚙️ TECHNICAL METHODOLOGY

### 📐 How Indicators are Classified

#### Leading Indicators
**Definition:** Forward-looking signals that typically turn 3-12 months before the economy.

**Categories:**
- **Financial Markets:** Yield curves, credit spreads, equity indices, VIX
- **Forward Orders:** ISM New Orders, Building Permits, Leading Economic Index
- **Sentiment:** Consumer/Business confidence, PMI surveys
- **Liquidity:** M2 Money Supply, Fed RRP

**Why they matter:** These are early warning systems. When Leading indicators weaken consistently, Coincident indicators (jobs, production) typically follow.

---

#### Coincident Indicators
**Definition:** Real-time measures of current economic activity.

**Categories:**
- **Labor:** Unemployment rate, Payrolls, Employment rate
- **Production:** Industrial Production, GDP
- **Consumption:** Retail Sales

**Why they matter:** These confirm whether the economy is currently expanding or contracting. They validate (or contradict) what Leading indicators predicted.

---

#### Lagging Indicators
**Definition:** Slow-moving confirmations that change after the economy has already shifted.

**Categories:**
- **Inflation:** CPI, HICP, Core inflation
- **Wages:** Average Hourly Earnings, Labor Cost Index
- **Policy:** Interest rates (as lagging confirmation of cycle position)
- **Credit:** Consumer credit growth

**Why they matter:** These lock in the macro regime. High inflation + tight labor = late cycle. Falling inflation + rising unemployment = recession confirmed.

---

### 📊 Percentile Calculation

**Purpose:** Translate raw indicator values into context: "Is this high, low, or normal?"

#### Two Windows:
1. **All-Time Percentile:** Compares current value to full available history
   - Example: CPI at 3.5% → 72nd percentile all-time → "Above average historically"

2. **5-Year Percentile:** Compares current value to recent 5 years only
   - Example: Same CPI at 3.5% → 45th percentile (5Y) → "Mid-range recently"

#### Why Both?
- **All-time** = Long-run context (is this extreme vs decades?)
- **5-year** = Recent regime (is this extreme vs current cycle?)

**Formula:**
```python
percentile = (count of historical values <= current value) / total count * 100
```

**Inverted Indicators:**
- For "bad-is-high" indicators (unemployment, spreads), percentiles are flipped
- High unemployment → Low percentile (bad signal)
- This ensures all percentiles point the same direction: **Higher = Stronger economy**

---

### 📈 Trend Calculation (6-Month Momentum)

**Purpose:** Identify whether an indicator is improving, deteriorating, or flat.

#### Methodology:

**Step 1: Compute Recent vs Historical Means**
```python
recent_mean = mean(last 6 months)
historical_mean = mean(full history OR last 5 years)
historical_std = std(full history OR last 5 years)
```

**Step 2: Calculate Z-Score**
```python
trend_z = (recent_mean - historical_mean) / historical_std
```

**Step 3: Label Trend**
| Z-Score Range | Trend Label | Interpretation |
|---------------|-------------|----------------|
| z > +1.0 | **Strong up ↗** | Recently much higher than normal |
| +0.5 < z ≤ +1.0 | **Mild up ↗** | Recently above normal |
| -0.5 ≤ z ≤ +0.5 | **Flat →** | Recently near normal |
| -1.0 ≤ z < -0.5 | **Mild down ↘** | Recently below normal |
| z < -1.0 | **Strong down ↘** | Recently much lower than normal |

**Requirements:**
- Needs **at least 6 months of recent data**
- No gaps > 90 days (for monthly indicators)
- If insufficient data → **"Trend unavailable"**

**Why 6 months?**
- Long enough to smooth noise
- Short enough to catch turning points before full-year averages
- Aligns with typical macro forecasting horizons

---

### 🎯 Macro State Aggregation

**Purpose:** Combine 10-20 individual indicators into one digestible state per category.

#### Logic (Per Region, Per Category):

**Step 1: Filter Indicators**
```python
indicators = [Leading/Coincident/Lagging for region]
exclude: hidden=True, contextual=True
```

**Step 2: Compute Average Percentile**
```python
avg_percentile = mean([ind.percentile_all for ind in indicators])
```

**Step 3: Classify State**
| Avg Percentile | State | Color | Interpretation |
|----------------|-------|-------|----------------|
| ≥ 65 | **Strong** 🟢 | Green | Most indicators elevated → expansion |
| 35-65 | **Neutral** ⚪ | Gray | Mixed signals → mid-cycle or transition |
| < 35 | **Weak** 🔴 | Red | Most indicators depressed → contraction risk |

#### Additional Nuance:
- **Mixed-High** 🟡: avg > 50 but high_count / total < 0.5 (some strong, some weak)
- **Softening** 🟠: avg < 50 but not yet Weak (early deterioration)

---

### 🔄 US vs Eurozone Macro Relative View

**Purpose:** Determine which region has a macro advantage for FX context.

#### Scoring System:

**Compare 4 Dimensions:**
1. **Growth Momentum:** Leading indicator avg percentile
   - Strong > Moderate > Weak
2. **Inflation Pressure:** CPI/HICP percentile
   - Lower = Better (subdued < moderate < elevated)
3. **Policy Stance:** Yield/rate percentile
   - Accommodative > Neutral > Restrictive (context-dependent)
4. **Recession Risk:** Coincident indicator avg percentile + Leading trends
   - Low > Moderate > Elevated

**Winner Determination:**
- US wins ≥2 dimensions → "US macro advantage" → **USD bias**
- EU wins ≥2 dimensions → "Eurozone macro advantage" → **EUR bias**
- Split evenly → "Macro divergence limited" → **Mixed/tactical**

**Output:**
- Headline (1 line)
- Paragraph (2-3 sentences, CFO language)
- Comparison table (4 dimensions)
- FX implication (1 sentence)

---

### 💬 Dynamic Interpretation System

**Purpose:** Auto-generate plain-English commentary for each indicator.

#### Three Layers:

**1. Fun Line (Catchy One-Liner)**
- Static per indicator
- Example: "The Fed whisper channel — where policy bets move first."

**2. Dynamic Line (What It Means Now)**
```python
def dynamic_interpretation(trend_label, percentile, type_tag):
    direction = trend_direction(trend_label)  # up/down/flat
    level = level_bucket(percentile)  # high/mid/low
    
    return f"{DIRECTION_PHRASE[type_tag][direction]} {LEVEL_PHRASE[level]}"
```
Example Output:
- "Expansion momentum is building from below-average levels."
- "Credit stress is easing but remains elevated."

**3. Trend Explainer**
```python
def trend_explainer(trend_label):
    if "up" in trend_label:
        return "Little net change over the last 6 months."
    elif "down" in trend_label:
        return "Falling steadily over recent months."
    else:
        return "Stable over the last 6 months."
```

**Result:** Every indicator card shows:
- Name + Fun Line
- Current Value + Date
- Percentiles (All-time, 5Y)
- Qualitative Label (derived from percentile)
- Dynamic Line (contextual interpretation)
- Trend Label + Explainer

---

### ⚖️ Inverted Indicators

**Problem:** Some indicators are "bad-is-high":
- Unemployment (high = bad)
- Credit spreads (high = stress)
- VIX (high = fear)

**Solution:** Flip percentiles so **all indicators point the same direction**.

**Implementation:**
```python
if indicator.inverted:
    display_percentile = 100 - raw_percentile
```

**Why?**
- Makes aggregation consistent (avg percentile = avg health)
- Visual consistency (green/high = good everywhere)
- Simplifies interpretation (no mental inversions)

**Flagged as Inverted:**
- Unemployment rates
- Credit spreads (HY, BBB, Euro HY)
- VIX, VXEEM
- Yield curves (when inverted = bad)

---

### 🔧 Derived Indicators (Spreads & Curves)

**Purpose:** Compute spreads from two FRED series on-the-fly.

**Examples:**
- **US Yield Curve:** DGS10 - DGS1 (10Y - 1Y Treasury)
- **EU Yield Curve:** IRLTLT01EZM156N - IRSTCI01EZM156N
- **FR-DE Spread:** IRLTLT01FRM156N - IRLTLT01DEM156N (OAT - Bund)

**Implementation:**
```python
'source': 'derived'  # NOT 'derived_file'
'spread_component_1': 'SERIES_A'
'spread_component_2': 'SERIES_B'
```

**Process:**
1. Fetch both component series from FRED (full history)
2. Align dates (inner join)
3. Compute spread = component_1 - component_2
4. Store as timeseries with full history
5. Trend engine can now calculate 6-month momentum

**Why Not 'derived_file'?**
- 'derived_file' expects pre-computed CSV with historical data
- We don't maintain those files → causes "Trend unavailable"
- 'derived' computes on-the-fly with full API data → works every time

---

### 📏 Display Units & Formatting

**Automatic Conversions:**

| Indicator Type | Raw Format | Display Format | Example |
|----------------|------------|----------------|---------|
| Inflation (YoY) | Index level | % YoY change | 3.2% YoY |
| Rates/Yields | Decimal | Percentage | 4.5% |
| Spreads | Basis points | Percentage or bp | 0.78% or 78bp |
| Labor Cost Index | Index level | YoY % change | 4.1% YoY |
| Employment (EA) | Thousands | Millions | 167.9M persons |
| GDP | Index level | QoQ % change | 2.5% QoQ |

**Special Cases:**
- **M2 Money Supply:** Auto-computed as YoY % change from level
- **Retail Sales:** If index, compute YoY; if already %, display as-is
- **Unemployment:** Already in %, display directly

---

## 🔄 REFRESH SUMMARY TABLE

| Component | Source | Auto-Update? | Frequency | Cache TTL | Action Needed |
|-----------|--------|--------------|-----------|-----------|---------------|
| **US Macro** | FRED API | ✅ Yes | Daily | 24 hours | None |
| **EU Macro (14)** | FRED API | ✅ Yes | Daily | 24 hours | None |
| **EU Macro (9)** | Static CSV | ❌ No | Manual | N/A | Update monthly |
| **EUR/USD Technical** | Yahoo Finance | ✅ Yes | Daily | 24 hours | None |
| **FX Valuation (L1)** | Trained Model | ❌ No | Quarterly | N/A | Run `RETRAIN_FX_MODELS.bat` |
| **FX Pressure (L2)** | Trained Model | ❌ No | Quarterly | N/A | Run `RETRAIN_FX_MODELS.bat` |
| **CFTC Positioning** | Static Sample | ❌ No | Manual | N/A | Implement auto-fetch |

---

## 📅 MAINTENANCE SCHEDULE

### Daily (Automatic)
- ✅ US Macro indicators (FRED)
- ✅ EU Macro indicators (FRED subset)
- ✅ EUR/USD Technical Analysis (Yahoo Finance)

### Weekly (Manual - Recommended)
- ⚠️ CFTC Positioning data (once auto-fetch is implemented)

### Monthly (Manual)
- ⚠️ Eurozone CSV indicators (9 files)
- Check for missing data / API failures

### Quarterly (Manual - FX Model Retraining)
- ⚠️ Retrain FX Valuation + Pressure models
- See detailed process below ↓

---

## 🔄 HOW TO RETRAIN FX MODELS

### When to Retrain

**Routine (Every Quarter):**
- End of March → Incorporate Q1 data
- End of June → Incorporate Q2 data
- End of September → Incorporate Q3 data
- End of December → Incorporate Q4 data

**Ad-Hoc (Regime Shift):**
- Fed/ECB policy pivot (rate cuts/hikes begin)
- Major crisis (2008-style, COVID-style)
- Model performance degrades (fair value diverging badly)

---

### Retraining Process (One-Click)

**Step 1:** Double-click the batch file
```
C:\Users\NikhilHanda\RETRAIN_FX_MODELS.bat
```

**What it does:**
1. Retrains Layer 1 (Monthly Valuation Model) → ~2-5 minutes
   - Fetches fresh monthly macro data (FRED API)
   - Engineers features (yield diffs, spreads, inflation)
   - Retrains Elastic Net model
   - Outputs: `elasticnet_predictions.csv`, `layer1_recommendation.json`

2. Retrains Layer 2 (Weekly Pressure Model) → ~3-7 minutes
   - Fetches weekly market data (yields, VIX, credit spreads)
   - Engineers weekly features (momentum, flow, volatility)
   - Retrains XGBoost model for Δz prediction
   - Outputs: `xgboost_delta_z_predictions.csv`, `layer2_recommendation.json`

3. Regenerates Decision Table + Charts → ~30 seconds
   - Combines Layer 1 + Layer 2 outputs
   - Generates decision table (Valuation × Pressure)
   - Creates 4 charts (Fair Value, Mispricing Z-Score, Pressure Panel, Decision Map)
   - Outputs: 1 JSON + 4 PNG files

4. Auto-copies outputs to GitHub folder
   - From: `C:\Users\NikhilHanda\FX Views\5_outputs\`
   - To: `C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\5_outputs\`

**Total Runtime:** ~5-10 minutes

---

**Step 2:** Open GitHub Desktop

You'll see **5 files changed** in `FX Views\5_outputs\`:
- `eurusd_fx_views_decision.json`
- `eurusd_fxviews_fair_value_monthly.png`
- `eurusd_fxviews_mispricing_z_monthly.png`
- `eurusd_fxviews_pressure_weekly.png`
- `eurusd_fxviews_decision_map.png`

---

**Step 3:** Commit + Push

**Commit message:**
```
Retrain FX models Q1 2025: Update valuation & pressure
```

Click **"Push origin"**

Streamlit Cloud auto-deploys in ~2 minutes.

---

**Step 4:** Verify on Dashboard

Visit: https://macro-dashboard-w4b8ydzlxgeowjnrkchvkd.streamlit.app/

Navigate to **FX Insights** → Check that:
- Fair Value updated
- Mispricing Z-score reflects latest data
- Charts show current month/week
- Decision table reflects new regime

---

## 🚨 KNOWN LIMITATIONS FOR V1.0

1. **No automated CFTC updates** - Static sample data
2. **9 Eurozone indicators require manual CSV updates** - Monthly cadence
3. **FX models are pre-trained** - Cannot adapt to regime shifts without retraining
4. **No alerting system** - Users must manually check dashboard
5. **No historical data download** - Dashboard is view-only

---

## 🧮 FX VALUATION & PRESSURE MODELS

### 🎯 Two-Layer Framework Design

**Philosophy:** Separate **macro valuation** (slow, monthly) from **tactical pressure** (fast, weekly).

---

#### Layer 1: Monthly Macro Valuation

**Purpose:** Estimate EUR/USD "fair value" based on fundamental drivers.

**Data Frequency:** Monthly  
**Features Used:**
- US vs EA 10-year yields (monthly)
- Inflation differential (CPI US - HICP EA, YoY)
- Credit spread differential (US BBB - EA BBB)
- Liquidity proxies (Fed RRP, ECB LTRO)
- Labor market indicators (unemployment rates)

**Model:** Elastic Net Regression (L1 + L2 regularization)
- **Why Elastic Net?** Balances interpretability (coefficient sparsity) with stability (handles multicollinearity)
- **Alternatives tested:** Ridge, Lasso, XGBoost single-stage, XGBoost two-stage residual
- **Selection criteria:** FV stability, regime frequency, economic coherence, RMSE (secondary), R² (informational)

**Outputs:**
1. **Fair Value (FV):** Model-estimated equilibrium EUR/USD
2. **Mispricing:** Spot - FV
3. **Mispricing Z-Score:** (Spot - FV) / σ_training
4. **Regime Label:**
   - **In-line:** |z| < 1.0
   - **Stretch:** 1.0 ≤ |z| < 2.0 (Cheap or Rich)
   - **Break:** |z| ≥ 2.0 (Cheap Break or Rich Break)

**Interpretation:**
- FV = 1.12, Spot = 1.05 → EUR is 7 cents **cheap** vs fundamentals
- z = -1.8σ → **Cheap Stretch** regime → mean reversion likely but not imminent

**Retraining Cadence:** Quarterly (or when regime shifts materially)

---

#### Layer 2: Weekly Pressure Signal

**Purpose:** Predict near-term direction of mispricing (expanding or compressing).

**Data Frequency:** Weekly  
**Features Used (NO monthly macro):**
- US vs Bund market yields (10Y, weekly changes)
- Credit spread changes (US HY, EA HY)
- Volatility (VIX, VXEEM weekly changes)
- Liquidity flow (Fed RRP weekly change)
- FX momentum (4-week returns, optional)

**Model:** XGBoost Regressor (predicting Δz)
- **Target:** Change in mispricing z-score week-over-week
- **Output:** Predicted Δz_hat
- **Classification:** Δz_hat < 0 → **Compress**, Δz_hat > 0 → **Expand**

**Why XGBoost here?**
- Captures non-linear interactions (volatility + flow regimes)
- Weekly data is noisier → ensemble handles better than Ridge
- Feature importances are interpretable

**Evaluation:**
- **Hit rate:** % of weeks where predicted direction = actual direction
- **Conditional performance:** Hit rate when |z| > 1σ (when signal matters most)

**Interpretation:**
- Pressure = **Compress** → Mispricing shrinking, mean reversion in progress
- Pressure = **Expand** → Mispricing widening, momentum dominating

---

### 🧩 Decision Table (Valuation × Pressure)

**Purpose:** Translate model outputs into actionable stance.

| Valuation | Pressure | Stance | Interpretation |
|-----------|----------|--------|----------------|
| **Cheap** (z < -1) | Compress | **Mean Reversion Setup** | Value + flow aligned → strong buy-dip case |
| **Cheap** (z < -1) | Expand | **Knife Catch Risk** | Value says buy, flow says wait → caution |
| **Fair** (\|z\| < 1) | Compress | **Range / Normalization** | Near fair, mispricing shrinking → neutral/range |
| **Fair** (\|z\| < 1) | Expand | **Trend Building** | Breakout setup, watch technicals |
| **Rich** (z > 1) | Compress | **Overvaluation Fading** | Fade rallies, mean reversion starting |
| **Rich** (z > 1) | Expand | **Momentum vs Value** | Rich and getting richer → late-cycle risk |

**Confidence Modifiers:**
- High confidence: Valuation + Pressure + Positioning aligned
- Medium confidence: V+P aligned, positioning neutral/unavailable
- Low confidence: V+P disagree

---

### 📊 CFTC Positioning (Risk Overlay)

**Purpose:** Measure crowding and asymmetry risk, NOT predict direction.

**Data Source:** CFTC Commitments of Traders (COT)  
**Asset:** EUR FX Futures (non-commercial speculative)  
**Frequency:** Weekly (released Friday, as-of Tuesday)

**Core Metrics:**
1. **Net Position:** Long contracts - Short contracts
2. **Z-Scores:** 
   - 6-month: (current_net - mean_6m) / std_6m
   - 1-year: (current_net - mean_1y) / std_1y
3. **Historical Percentile:** vs full available history

**Classification:**
- **Crowded Long:** z > +1.5 OR percentile > 85
- **Crowded Short:** z < -1.5 OR percentile < 15
- **Neutral:** Otherwise

**Interpretation:**
- **Crowded Long:** Downside asymmetry rising, sensitive to negative surprises
- **Crowded Short:** Squeeze risk if macro/policy turns supportive
- **Neutral:** Limited crowding-related risk

**⚠️ NOT used for:** Price targets, expected returns, mean reversion timing

---

### 📐 Technical Analysis (Price Only)

**Purpose:** Answer "when" (not "why") using pure price behavior.

**Data:** EUR/USD daily OHLC (Yahoo Finance)  
**Refresh:** Hourly (cache TTL = 3600s)

**Indicators:**
- **Moving Averages:** 50d, 100d, 200d
- **Momentum:** RSI (14), MACD (12,26,9)
- **Volatility:** Bollinger Bands (20,2), ATR (20)
- **Anchors:** 1-year high/low, Fibonacci (38.2, 50, 61.8)

**Technical Bias Scoring:**

**Structure Score (S):** [-2.5, +2.5]
- Spot vs 200d MA: ±1.0
- Spot vs 100d MA: ±0.5
- Spot vs 50d MA: ±0.5
- Spot vs Fib 50%: ±0.5

**Momentum/Volatility Score (M):** [-3.0, +3.0]
- RSI: ±1.0 (bullish >55, bearish <45)
- MACD histogram: ±1.0 (rising/falling)
- Bollinger width: ±0.5 (coiled → breakout potential)
- ATR exhaustion: -0.5 (extreme volatility → reversal risk)

**Final Technical Bias:**
```python
S_norm = S / 2.5  # [-1, +1]
M_norm = M / 3.0  # [-1, +1]
technical_bias = 3.0 * (0.5*S_norm + 0.5*M_norm)  # [-3, +3]
```

**Regime:**
- Bias ≥ +1.5 → **Bullish**
- -1.5 < Bias < +1.5 → **Neutral**
- Bias ≤ -1.5 → **Bearish**

**Confirmation Status (Separate):**
- **Confirmed:** Spot vs MA alignment + MACD momentum + Bollinger/1Y breakout
- **Not confirmed:** Structure without follow-through

**Trade Posture (Action-Oriented):**
- **Buy Breakouts:** Bullish + Confirmed + Volatility expanding
- **Fade Rallies:** Bearish bias + Low volatility
- **Sell Breakdowns:** Bearish + Confirmed + Momentum accelerating
- **Range / Wait:** Neutral bias OR unconfirmed

**Key Levels (Top 5 only):**
1. 200d MA (primary trend anchor)
2. Nearest Fib level
3. 100d MA
4. 1Y high/low (whichever closer)
5. 50d MA

---

### 🔗 Fusion Layer: "Nikhil's FX Commentary"

**Purpose:** Combine Valuation + Technicals + Positioning into one natural paragraph.

**Inputs:**
- **Valuation:** state (rich/cheap/fair), trend (widening/stabilizing/compressing)
- **Technicals:** bias (-3 to +3), posture (buy/fade/wait), confirmation
- **Positioning:** state (crowded/neutral), risk contribution

**Output Format:** 3-5 sentence flowing paragraph (no bullets, no labels)

**Confidence Logic:**
- **High:** V+T agree + positioning aligned/neutral + both modules have data
- **Medium:** V+T agree but positioning unavailable OR V+T weak agree
- **Low:** V+T disagree OR data quality issues

**Example Output:**
> *EUR looks moderately rich vs macro fundamentals, though that overvaluation has stopped widening. Technicals show constructive price structure but lack confirmation, keeping the bias tentative. Positioning is neutral, so crowding isn't constraining price action either way. Net view: This setup favors fading rallies rather than chasing strength, but watch for technical confirmation before committing.*

**Two Modes:**
1. **Analyst Mode:** Includes indicators, specific levels, technical jargon
2. **Executive Mode:** Risk framing only, no levels, CFO-friendly language

---

## 🎨 UI/UX DESIGN PRINCIPLES

### Progressive Disclosure (Macro Page)

**Problem Solved:** 20+ indicators on one page = overwhelming.

**Solution:** Three-layer hierarchy with optional deep-dive.

#### Layer 1: Narrative (Always Visible)
- **What:** Nikhil's voice, no data clutter
- **Purpose:** Orientation before touching data
- **Format:** 2-4 sentence paragraph explaining current macro state
- **Example:** *"US macro momentum is rolling over. Leading indicators are softening, coincident data is flat, and lagging inflation remains sticky..."*

#### Layer 2: Macro State Summary (Scan Layer)
- **What:** Three boxes (Leading / Coincident / Lagging)
- **Each shows:** Color-coded state (Strong 🟢 / Neutral ⚪ / Weak 🔴) + one-line caption
- **Purpose:** Answer "where are we in the cycle?" at a glance
- **Example:** Leading 🟡 Softening | Coincident ⚪ Flat | Lagging 🟢 Tight

#### Layer 3: Indicator Explorer (Optional, Collapsed by Default)
- **What:** Full indicator library, grouped by category
- **Format:** Accordion-style collapsible groups
  - ▶ Leading Indicators (14)
  - ▶ Coincident Indicators (5)
  - ▶ Lagging Indicators (4)

**Each Indicator Has Two States:**

**Collapsed State (Default):**
- Name + category tag
- Latest value + date
- State label (e.g., "Very High → easing")
- Momentum arrow (↗ ↘ →)
- **No charts, no percentile bars** → scannable

**Expanded State (On Click):**
- Full historical line chart
- Percentile bands (all-time, 5-year)
- 3-line description:
  1. What it measures (1 sentence)
  2. Why FX cares (1 sentence)
  3. Current signal (1 sentence)
- Trend explainer

**Global Toggle:** "Explore Mode" checkbox (sidebar)
- OFF (default): All collapsed
- ON: All expanded (for power users)

**Result:** 
- CFO sees narrative + state → done in 10 seconds
- Analyst expands 3-5 key indicators → targeted deep-dive
- No one drowns in 20 charts at once

---

### Dashboard Navigation Structure

**Top Level:**
1. **Macro View** (home page)
   - Region selector: US / Eurozone buttons
   - Macro Relative View (US vs EUR comparison for FX context)
   - Single-region drill-down

2. **FX Insights** (sidebar page)
   - Top: Nikhil's FX Commentary (fusion layer)
   - Commentary Mode Toggle: Analyst / Executive
   - Three horizontal tabs:
     - **Valuation** (Layer 1 model + Layer 2 pressure)
     - **Technicals** (price-only indicators)
     - **Positioning** (CFTC speculative net)

**Design Principle:** 
- **Default to insight** (narrative first)
- **Reveal complexity on demand** (charts/indicators optional)
- **Consistent dialect** (all modules use score + state + confirmation language)

---

### Color & Visual Language

**Macro Health:**
- 🟢 Green = Strong (avg percentile ≥ 65)
- ⚪ Gray = Neutral (35-65)
- 🔴 Red = Weak (< 35)
- 🟡 Yellow = Mixed/Softening (transition states)

**FX Modules (Accent Colors):**
- **Valuation:** Muted amber/yellow (`#FFB84D`, `#8B6914`)
- **Technicals:** Blue (`#4A9EFF`, `#1E3A5F`)
- **Positioning:** Purple/teal (`#9B59B6`, `#16A085`)

**Typography Hierarchy:**
- **Narrative:** Largest, most prominent
- **State Summary:** Medium, color-coded boxes
- **Indicator Details:** Smallest, technical

**Why Consistent?**
- Users learn the visual system once, apply everywhere
- Color = instant signal (no need to read labels)
- Hierarchy = prioritizes decision-making over data tourism

---

## 📞 DATA ISSUES & TROUBLESHOOTING

### Indicator Missing / "No data" Error
**Cause:** FRED API rate limit, series discontinued, or bad series ID  
**Fix:** Check FRED website for series status, retry after 1 hour

### Eurozone Indicators Fail to Load
**Cause:** CSV files missing or corrupted  
**Fix:** Check `eurozone_data/` folder, re-download from source

### Technical Analysis Shows Stale Data
**Cause:** Yahoo Finance API failure or cache not clearing  
**Fix:** Click "Clear Cache" button in sidebar, refresh page

### CFTC Data Never Updates
**Cause:** Not implemented yet (V1.0 limitation)  
**Fix:** Wait for V1.1 auto-fetch implementation

---

## 📚 DATA SOURCE LINKS

- **FRED API:** https://fred.stlouisfed.org/
- **Eurostat Data Browser:** https://ec.europa.eu/eurostat/data/database
- **CFTC COT Reports:** https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
- **Yahoo Finance:** https://finance.yahoo.com/quote/EURUSD=X

---

**Version History:**
- V1.2 (Dec 24, 2024): Added FX model retraining process, updated cache settings (technicals 1h→24h), fixed GDP series
- V1.1 (Dec 23, 2024): Added comprehensive technical methodology, FX model details, UI/UX design principles
- V1.0 (Dec 22, 2024): Initial production documentation

