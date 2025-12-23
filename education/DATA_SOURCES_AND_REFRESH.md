# Macro View Dashboard - Data Sources & Refresh Schedule

**Last Updated:** December 22, 2024  
**Production Version:** 1.0

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
| Real GDP (QoQ) | GDPC1 | Quarterly | Economic growth |

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

## 🔄 REFRESH SUMMARY TABLE

| Component | Source | Auto-Update? | Frequency | Cache TTL | Action Needed |
|-----------|--------|--------------|-----------|-----------|---------------|
| **US Macro** | FRED API | ✅ Yes | Daily | 24 hours | None |
| **EU Macro (14)** | FRED API | ✅ Yes | Daily | 24 hours | None |
| **EU Macro (9)** | Static CSV | ❌ No | Manual | N/A | Update monthly |
| **EUR/USD Technical** | Yahoo Finance | ✅ Yes | Hourly | 1 hour | None |
| **FX Valuation (L1)** | Static Predictions | ❌ No | Manual | N/A | Retrain quarterly |
| **FX Pressure (L2)** | Static Predictions | ❌ No | Manual | N/A | Retrain quarterly |
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

### Quarterly (Manual)
- ⚠️ Retrain FX Valuation models
- ⚠️ Regenerate Layer 1 & 2 predictions
- Review indicator selection / model performance

---

## 🚨 KNOWN LIMITATIONS FOR V1.0

1. **No automated CFTC updates** - Static sample data
2. **9 Eurozone indicators require manual CSV updates** - Monthly cadence
3. **FX models are pre-trained** - Cannot adapt to regime shifts without retraining
4. **No alerting system** - Users must manually check dashboard
5. **No historical data download** - Dashboard is view-only

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
- V1.0 (Dec 22, 2024): Initial production documentation

