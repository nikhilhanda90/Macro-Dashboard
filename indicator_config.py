"""
Indicator Configuration - Single Source of Truth
All US indicators with metadata for trend computation and interpretation
"""

import pandas as pd
import numpy as np

# ============================================================================
# US INDICATOR CONFIG TABLE
# ============================================================================

US_INDICATOR_CONFIG = [
    # LEADING (14)
    {"series_id": "T10Y3M", "name": "10Y-3M Yield Curve", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "yield_curve_slope", "trend_method": "level", "region": "US"},
    {"series_id": "BAMLH0A0HYM2", "name": "High Yield Spread", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "credit_spread", "trend_method": "level", "region": "US"},
    {"series_id": "BAMLC0A4CBBB", "name": "BBB Corporate Spread", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "credit_spread", "trend_method": "level", "region": "US"},
    {"series_id": "T10YIEM", "name": "10Y Breakeven Inflation", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation_expectation", "trend_method": "level", "region": "US"},
    {"series_id": "DFII10", "name": "10Y Real Rate (TIPS)", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "real_rate", "trend_method": "level", "region": "US"},
    {"series_id": "DGS1", "name": "1Y Treasury Rate", "bucket": "leading", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "US"},
    {"series_id": "HOUST", "name": "Housing Starts", "bucket": "leading", "category": "Housing", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "housing_activity", "trend_method": "level", "region": "US"},
    {"series_id": "MSACSR", "name": "Months Supply New Houses", "bucket": "leading", "category": "Housing", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "housing_slack", "trend_method": "level", "region": "US"},
    {"series_id": "MANEMP", "name": "ISM Manufacturing PMI", "bucket": "leading", "category": "Growth", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "US"},
    {"series_id": "NEWORDER", "name": "ISM Manufacturing New Orders", "bucket": "leading", "category": "Growth", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "US"},
    {"series_id": "AWHMAN", "name": "Avg Weekly Hours - Manufacturing", "bucket": "leading", "category": "Labor", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "labor_quantity", "trend_method": "level", "region": "US"},
    {"series_id": "UMCSENT", "name": "Consumer Sentiment (U of M)", "bucket": "leading", "category": "Sentiment", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "sentiment", "trend_method": "level", "region": "US"},
    {"series_id": "DRTSCILM", "name": "Bank Lending Standards", "bucket": "leading", "category": "Credit", "frequency": "quarterly", "use_yoy": False, "use_mom": False, "inverted": True, "type_tag": "lending_standards", "trend_method": "level", "region": "US"},
    {"series_id": "VIXCLS", "name": "VIX (Equity Volatility)", "bucket": "leading", "category": "Market", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": True, "type_tag": "volatility_risk_off", "trend_method": "level", "region": "US"},
    {"series_id": "^GSPC", "name": "S&P 500", "bucket": "leading", "category": "Market", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "US"},
    {"series_id": "^IXIC", "name": "NASDAQ Composite", "bucket": "leading", "category": "Market", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "US"},
    
    # COINCIDENT (9)
    {"series_id": "PAYEMS", "name": "Nonfarm Payrolls", "bucket": "coincident", "category": "Labor", "frequency": "monthly", "use_yoy": False, "use_mom": True, "inverted": False, "type_tag": "labor_quantity", "trend_method": "mom", "region": "US"},
    {"series_id": "INDPRO", "name": "Industrial Production", "bucket": "coincident", "category": "Growth", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "US"},
    {"series_id": "RSXFS", "name": "Retail Sales", "bucket": "coincident", "category": "Growth", "frequency": "monthly", "use_yoy": True, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "yoy", "region": "US"},
    {"series_id": "PCECC96", "name": "Real Personal Consumption", "bucket": "coincident", "category": "Growth", "frequency": "quarterly", "use_yoy": True, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "yoy", "region": "US"},
    {"series_id": "DFF", "name": "Federal Funds Rate", "bucket": "coincident", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "US"},
    {"series_id": "SOFR", "name": "SOFR", "bucket": "coincident", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "US"},
    {"series_id": "MORTGAGE30US", "name": "30Y Mortgage Rate", "bucket": "coincident", "category": "Housing", "frequency": "weekly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "mortgage_rate", "trend_method": "level", "region": "US"},
    {"series_id": "RRPONTSYD", "name": "Reverse Repo", "bucket": "coincident", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "liquidity", "trend_method": "level", "region": "US"},
    {"series_id": "DTWEXBGS", "name": "Dollar Index", "bucket": "coincident", "category": "Fixed Income", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "fx_index", "trend_method": "level", "region": "US"},
    
    # LAGGING (6)
    {"series_id": "UNRATE", "name": "Unemployment Rate", "bucket": "lagging", "category": "Labor", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "labor_slack", "trend_method": "level", "region": "US"},
    {"series_id": "CPIAUCSL", "name": "CPI All Items", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "yoy", "region": "US"},
    {"series_id": "CPILFESL", "name": "Core CPI", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "yoy", "region": "US"},
    {"series_id": "PCEPI", "name": "PCE Price Index", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "yoy", "region": "US"},
    {"series_id": "PCEPILFE", "name": "Core PCE", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "yoy", "region": "US"},
    {"series_id": "ECIWAG", "name": "Employment Cost Index", "bucket": "lagging", "category": "Labor", "frequency": "quarterly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "wages_costs", "trend_method": "level", "region": "US"},
    
    # =============================================================================
    # EUROZONE INDICATORS
    # =============================================================================
    
    # LEADING (7)
    {"series_id": "IRSTCI01EZM156N", "name": "1Y Euro Yield", "bucket": "leading", "category": "Fixed Income", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    {"series_id": "IRLTLT01EZM156N", "name": "10Y Euro Long-Term Yield", "bucket": "leading", "category": "Fixed Income", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    {"series_id": "IRLTLT01DEM156N", "name": "German 10Y Bund", "bucket": "leading", "category": "Fixed Income", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    {"series_id": "IRLTLT01FRM156N", "name": "French 10Y OAT", "bucket": "leading", "category": "Fixed Income", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    # EA_YIELD_CURVE removed - duplicate of IRLTLT01EZM156N
    {"series_id": "BAMLHE00EHYIEY", "name": "Euro HY Corporate Spread", "bucket": "leading", "category": "Credit", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "credit_spread", "trend_method": "level", "region": "Eurozone", "cluster": "Credit & Risk"},
    {"series_id": "EUROSTAT_ESI_EA", "name": "Economic Sentiment Index", "bucket": "leading", "category": "Sentiment", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "sentiment", "trend_method": "level", "region": "Eurozone", "cluster": "Sentiment"},
    {"series_id": "EUROSTAT_CCI_EA", "name": "Consumer Confidence", "bucket": "leading", "category": "Sentiment", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "sentiment", "trend_method": "level", "region": "Eurozone", "cluster": "Sentiment"},
    {"series_id": "EA_INDUSTRIAL_CONF", "name": "Industrial Confidence (EA)", "bucket": "leading", "category": "Sentiment", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "sentiment", "trend_method": "level", "region": "Eurozone", "cluster": "Sentiment"},
    {"series_id": "^STOXX50E", "name": "Euro Stoxx 50", "bucket": "leading", "category": "Market", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "Eurozone", "cluster": "Credit & Risk"},
    
    # COINCIDENT (3)
    {"series_id": "LRHUTTTTEA156S", "name": "Unemployment Rate (EUR)", "bucket": "coincident", "category": "Labor", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": True, "type_tag": "labor_slack", "trend_method": "level", "region": "Eurozone", "cluster": "Labor & Wages"},
    {"series_id": "EA19PRINTO01IXOBM", "name": "Industrial Production (EUR)", "bucket": "coincident", "category": "Growth", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "Eurozone", "cluster": "Growth & Demand"},
    {"series_id": "NAEXKP01EZQ657S", "name": "Real GDP (EA)", "bucket": "coincident", "category": "Growth", "frequency": "quarterly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "growth_activity", "trend_method": "level", "region": "Eurozone", "cluster": "Growth & Demand"},
    {"series_id": "VXEEMCLS", "name": "EM Volatility Index", "bucket": "coincident", "category": "Market", "frequency": "daily", "use_yoy": False, "use_mom": False, "inverted": True, "type_tag": "volatility_risk_off", "trend_method": "level", "region": "Eurozone", "cluster": "Credit & Risk"},
    
    # LAGGING (3)
    {"series_id": "EA_HICP_HEADLINE", "name": "HICP Headline (EUR)", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    {"series_id": "CP0000EZ19M086NEST", "name": "HICP All Items (FRED)", "bucket": "lagging", "category": "Inflation", "frequency": "monthly", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "inflation", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    {"series_id": "ECBDFR", "name": "ECB Deposit Rate", "bucket": "lagging", "category": "Fixed Income", "frequency": "irregular", "use_yoy": False, "use_mom": False, "inverted": False, "type_tag": "policy_rate", "trend_method": "level", "region": "Eurozone", "cluster": "Inflation & Rates"},
    
    # ==========================
    # UK INDICATORS - REMOVED FOR V1
    # UK data quality on FRED is poor and requires ONS + BoE API integration (Phase 2)
    # ==========================
]

# ============================================================================
# INTERPRETATION RULES
# ============================================================================

INTERPRETATION_RULES = {
    "inflation": {
        "up": "Price pressures are building — more hawkish pressure on the central bank.",
        "down": "Price pressures are easing — more room for the central bank to stay dovish or cut.",
        "flat": "Price pressures are broadly stable versus last year.",
    },
    "inflation_expectation": {
        "up": "Market-based inflation expectations are rising — can feed into wage demands and pricing.",
        "down": "Inflation expectations are cooling — helpful for disinflation and policy flexibility.",
        "flat": "Inflation expectations are anchored and stable.",
    },
    "policy_rate": {
        "up": "Policy is tightening or staying restrictive; financing conditions are getting tougher.",
        "down": "Policy is easing or less restrictive; financing conditions are loosening.",
        "flat": "Policy stance is broadly unchanged.",
    },
    "real_rate": {
        "up": "Real funding conditions are tightening — good for the inflation fight, tougher on growth and risk assets.",
        "down": "Real funding conditions are easing — more supportive for growth and risk assets if inflation behaves.",
        "flat": "Real funding conditions are roughly unchanged.",
    },
    "yield_curve_slope": {
        "up": "The yield curve is steepening — usually a sign of easing recession risk and more normal term structure.",
        "down": "The yield curve is flattening or inverting — often a warning sign for future growth.",
        "flat": "The shape of the yield curve is little changed.",
    },
    "credit_spread": {
        "up": "Credit stress is rising; markets are demanding more compensation for risk.",
        "down": "Credit conditions are easing; markets are more comfortable taking credit risk.",
        "flat": "Credit spreads are stable.",
    },
    "growth_activity": {
        "up": "Real activity is picking up — growth momentum is strengthening.",
        "down": "Real activity is cooling — growth momentum is weakening.",
        "flat": "Growth indicators are broadly stable.",
    },
    "labor_quantity": {
        "up": "Job creation and labor demand are strengthening — supportive for income and spending.",
        "down": "Job growth is cooling — labor demand is softening.",
        "flat": "Job growth is broadly similar to last year.",
    },
    "labor_slack": {
        "up": "Labor market slack is rising — higher recession risks, lower wage pressure.",
        "down": "Labor slack is falling — tighter labor markets and more wage pressure.",
        "flat": "Labor slack is roughly unchanged.",
    },
    "wages_costs": {
        "up": "Labor costs are rising faster — potential margin pressure and sticky inflation.",
        "down": "Wage pressures are easing — less margin squeeze and inflation risk.",
        "flat": "Wage growth is roughly in line with recent history.",
    },
    "housing_activity": {
        "up": "Housing activity is picking up — supportive for construction and household wealth.",
        "down": "Housing activity is cooling — less support from construction and prices.",
        "flat": "Housing activity is broadly stable.",
    },
    "housing_slack": {
        "up": "Housing inventory is building — more slack and downward price pressure.",
        "down": "Housing inventory is tightening — less slack and upward price pressure.",
        "flat": "Housing inventory is broadly stable.",
    },
    "mortgage_rate": {
        "up": "Mortgage borrowing costs are rising — a headwind to housing demand.",
        "down": "Mortgage borrowing costs are falling — a tailwind for housing demand.",
        "flat": "Mortgage rates are little changed.",
    },
    "sentiment": {
        "up": "Confidence is improving — households and firms are more willing to spend and invest.",
        "down": "Confidence is deteriorating — more caution in spending and investment.",
        "flat": "Sentiment is broadly steady.",
    },
    "volatility_risk_off": {
        "up": "Market risk aversion is rising — a more risk-off environment.",
        "down": "Risk aversion is falling — a more risk-on environment.",
        "flat": "Market risk appetite is little changed.",
    },
    "lending_standards": {
        "up": "Banks are tightening lending standards — credit is harder to get.",
        "down": "Banks are easing lending standards — credit is easier to access.",
        "flat": "Bank lending standards are broadly unchanged.",
    },
    "fx_index": {
        "up": "The dollar is strengthening — tighter global USD conditions and pressure on non-USD borrowers.",
        "down": "The dollar is weakening — easier USD conditions and relief for non-USD borrowers.",
        "flat": "The dollar is broadly stable.",
    },
    "liquidity": {
        "up": "Use of the facility is rising — signaling more demand for safe/liquid assets.",
        "down": "Use of the facility is falling — less demand for that liquidity backstop.",
        "flat": "Use of the facility is fairly stable.",
    },
}

# ============================================================================
# FUN ONE-LINERS - Quick catchy description
# ============================================================================

INDICATOR_FUN_LINE = {
    # LEADING
    "T10Y3M":      "The bond market's recession early-warning siren.",
    "BAMLH0A0HYM2":"Wall Street's stress barometer for risky borrowers.",
    "BAMLC0A4CBBB":"The heartbeat of corporate credit conditions.",
    "T10YIEM":     "The market's long-term inflation mood ring.",
    "DFII10":      "The economy's real cost of money.",
    "DGS1":        "The short-term pulse of Fed policy expectations.",
    "HOUST":       "America's construction engine turning on or off.",
    "MSACSR":      "A quick read on housing tightness.",
    "MANEMP":      "The factory floor's confidence meter.",
    "NEWORDER":    "Manufacturers' forward-demand crystal ball.",
    "AWHMAN":      "Businesses' first hint of hiring or firing plans.",
    "UMCSENT":     "How optimistic the American household feels today.",
    "DRTSCILM":    "How easy banks are making it to get money.",
    "VIXCLS":      "The market's fear thermostat.",
    "^GSPC":       "America's stock market benchmark.",
    "^IXIC":       "The tech-heavy growth indicator.",
    
    # COINCIDENT
    "PAYEMS":      "The monthly scoreboard for job creation.",
    "INDPRO":      "A snapshot of how busy U.S. factories really are.",
    "RSXFS":       "The country's checkout-counter mood.",
    "PCECC96":     "The engine driving most of America's GDP.",
    "DFF":         "The benchmark steering every dollar borrowed.",
    "SOFR":        "Today's foundation for floating-rate markets.",
    "MORTGAGE30US":"The gatekeeper of American home affordability.",
    "RRPONTSYD":   "A pulse check on dollar liquidity demand.",
    "DTWEXBGS":    "A scoreboard for global dollar strength.",
    
    # LAGGING
    "UNRATE":      "The cleanest snapshot of labor slack.",
    "CPIAUCSL":    "The broadest read on consumer price inflation.",
    "CPILFESL":    "Inflation stripped of its noisy bits.",
    "PCEPI":       "The inflation gauge tied closest to spending.",
    "PCEPILFE":    "The Fed's favorite inflation compass.",
    "ECIWAG":      "A gauge of wage pressure under the hood.",
    
    # EUROZONE LEADING
    "IRSTCI01EZM156N": "A read on near-term Euro policy expectations.",
    "IRLTLT01EZM156N": "The Eurozone's long-term borrowing benchmark.",
    "IRLTLT01DEM156N": "Germany's risk-free rate for the Eurozone.",
    "IRLTLT01FRM156N": "France's borrowing cost premium vs Germany.",
    # EA_YIELD_CURVE removed
    "BAMLHE00EHYIEY":  "Europe's corporate stress barometer.",
    "EUROSTAT_ESI_EA": "A broad mood check on the Eurozone economy.",
    "EUROSTAT_CCI_EA": "How the European household feels about the future.",
    "EA_INDUSTRIAL_CONF": "A gut check from Europe's factory managers.",
    "^STOXX50E":   "Europe's blue-chip equity pulse.",
    
    # EUROZONE COINCIDENT
    "LRHUTTTTEA156S": "Europe's most direct read on labor slack.",
    "EA19PRINTO01IXOBM": "How busy European factories really are.",
    "NAEXKP01EZQ657S": "The Eurozone's broad economic growth scorecard.",
    "VXEEMCLS":        "A quick read on global risk appetite hitting Europe.",
    
    # EUROZONE LAGGING
    "EA_HOUSE_PRICES": "A slow-moving gauge of Eurozone housing health.",
    "LCEAMN01EZQ661S": "Wage pressure baked into employer costs.",
    "EA_HICP_HEADLINE": "The Eurozone's broadest inflation indicator.",
    "CP0000EZ19M086NEST": "The Eurozone's broadest inflation gauge.",
    "CPHPLA01EZM661N":  "Eurozone core inflation stripped of volatile items.",
    "ECBDFR":          "The ECB's anchor for Eurozone short-term rates.",
    
    # UK indicators removed (Phase 2)
}

# ============================================================================
# HOVER NARRATIVES - What the indicator measures (detailed)
# ============================================================================

INDICATOR_NARRATIVES = {
    "T10Y3M": "The spread between 10-year and 3-month Treasury yields. A steep curve (positive) signals growth expectations; an inverted curve (negative) has preceded every US recession since 1950. The most reliable leading indicator of economic turning points.",
    
    "BAMLH0A0HYM2": "ICE BofA High Yield Corporate Bond spread over comparable Treasuries. Measures credit risk premium for below-investment-grade borrowers. Rising spreads signal deteriorating credit conditions and risk-off sentiment.",
    
    "BAMLC0A4CBBB": "ICE BofA BBB Corporate Bond spread. The BBB rating is the lowest investment-grade tier—widening here signals stress migrating from junk to quality credits, often a late-cycle warning.",
    
    "T10YIEM": "Market-implied inflation expectations over the next 10 years. Derived from the spread between nominal and inflation-protected Treasuries. Rising breakevens suggest investors expect higher future inflation, often prompting tighter monetary policy. A key forward-looking gauge for Fed policy stance.",
    
    "DFII10": "The real (inflation-adjusted) yield on 10-year TIPS. Represents the after-inflation return investors demand. Higher real rates make borrowing expensive and slow growth; negative real rates stimulate risk-taking and investment. Critical for equity valuations and credit conditions.",
    
    "DGS1": "1-year Treasury constant maturity rate. Sits between Fed funds (overnight) and longer-term yields, capturing near-term policy expectations. Rising 1Y rates tighten financial conditions before impacting the real economy, making it a leading signal for credit and growth.",
    
    "HOUST": "New privately-owned housing units started (thousands, SAAR). A leading indicator of construction activity, household formation expectations, and consumer confidence. Housing starts lead employment in construction and durable goods.",
    
    "MSACSR": "Months of supply of new houses for sale at the current sales pace. Rising inventory signals weakening demand or overbuilding; falling inventory suggests tight supply and upward price pressure.",
    
    "MANEMP": "ISM Manufacturing Purchasing Managers' Index. Above 50 signals expansion; below 50 signals contraction. Surveys purchasing managers on new orders, production, employment, deliveries, and inventories—a timely read on factory activity.",
    
    "NEWORDER": "ISM Manufacturing New Orders Index. The most forward-looking component of the ISM report. Rising new orders signal future production increases; falling orders warn of slowdowns ahead.",
    
    "AWHMAN": "Average weekly hours worked in manufacturing. When demand softens, employers cut hours before cutting jobs. Rising hours can signal impending hiring; falling hours warn of layoffs ahead.",
    
    "UMCSENT": "University of Michigan Consumer Sentiment Index (1966:Q1=100). Measures household confidence about personal finances and the broader economy. Strong predictor of consumer spending, which drives ~70% of US GDP.",
    
    "DRTSCILM": "Net percentage of domestic banks reporting tightening lending standards for commercial & industrial loans. Rising values indicate credit is harder to obtain, slowing business investment and working capital. A leading indicator of credit availability.",
    
    "VIXCLS": "CBOE Volatility Index (VIX). Measures implied volatility of S&P 500 options—a gauge of market fear. Spikes indicate stress and flight to safety; low readings suggest complacency. Inverted for cycle scoring (high VIX = stress).",
    
    "^GSPC": "S&P 500 Index. The benchmark for US large-cap equities, covering ~500 of the largest US companies. Represents ~80% of total US market cap. Leading indicator for economic confidence, corporate earnings expectations, and risk appetite. Rising markets signal optimism; falling markets often precede economic weakness.",
    
    "^IXIC": "NASDAQ Composite Index. Heavily weighted toward technology, internet, and growth stocks. More volatile than S&P 500 but often leads directional changes. Strong performance indicates risk-on sentiment and confidence in future growth; weakness signals flight to quality and recession fears.",
    
    "PAYEMS": "Total nonfarm payroll employment (thousands). The headline jobs number. Month-over-month changes show labor demand strength. Strong payrolls support income growth and consumer spending; weak payrolls warn of recession.",
    
    "INDPRO": "Industrial Production Index (2017=100). Measures real output of factories, mines, and utilities. A broad gauge of goods-producing activity and manufacturing health.",
    
    "RSXFS": "Advance Retail Sales (millions, not seasonally adjusted). Captures consumer spending on goods (excludes services). YoY growth shows the strength of household consumption, the largest GDP component.",
    
    "PCECC96": "Real Personal Consumption Expenditures (billions, chained 2017 dollars, SAAR). The Fed's preferred measure of consumer spending adjusted for inflation. YoY growth tracks the health of the consumer—the economy's main engine.",
    
    "DFF": "Effective Federal Funds Rate. The overnight interbank lending rate targeted by the Federal Reserve. The primary tool of US monetary policy. Rising rates tighten financial conditions; falling rates ease them.",
    
    "SOFR": "Secured Overnight Financing Rate. Replaced LIBOR as the key short-term rate benchmark. Based on Treasury repo transactions. Reflects actual money market conditions and Fed policy transmission.",
    
    "MORTGAGE30US": "30-year fixed-rate mortgage average (percent). The borrowing cost for most US homebuyers. Rising rates dampen affordability and housing demand; falling rates stimulate purchases and refinancing.",
    
    "RRPONTSYD": "Overnight Reverse Repurchase Agreements at the Federal Reserve (billions). Banks and money market funds park cash here. High usage signals excess liquidity and tight money market conditions; falling usage suggests easing liquidity.",
    
    "DTWEXBGS": "Trade Weighted US Dollar Index: Broad, Goods and Services. Measures the dollar against a basket of major currencies. A rising dollar tightens global financial conditions and pressures emerging markets; a falling dollar eases them.",
    
    "UNRATE": "Unemployment Rate (percent of labor force). Lags the cycle—rises after recessions start and falls after recoveries are underway. Persistent increases signal labor market distress.",
    
    "CPIAUCSL": "Consumer Price Index for All Urban Consumers (1982-84=100). The headline inflation measure. Includes food and energy. YoY growth tracks cost-of-living changes and drives inflation expectations.",
    
    "CPILFESL": "Core CPI (excludes food and energy). Strips out volatile components to reveal underlying inflation trends. The Fed watches this closely for persistent price pressures.",
    
    "PCEPI": "Personal Consumption Expenditures Price Index (2017=100). The Fed's preferred inflation gauge. Broader and less volatile than CPI. YoY growth is the key metric for the Fed's 2% target.",
    
    "PCEPILFE": "Core PCE (excludes food and energy). The single most important inflation series for Fed policy. YoY growth around 2% is the Fed's mandate. Above signals hawkish pressure; below allows dovish ease.",
    
    "ECIWAG": "Employment Cost Index: Wages and Salaries (2005=100). Measures labor cost growth including benefits. Lags the cycle but captures wage pressure that can feed persistent inflation.",
    
    # EUROZONE
    "IR3TIB01EZM156N": "3-month Euro Interbank Offered Rate. The short-term funding rate for European banks. Closely tracks ECB policy and money market conditions in the Euro area.",
    
    "IRSTCI01EZM156N": "1-year Euro Area government bond yield. Reflects near-term policy rate expectations and short-term borrowing costs across the Eurozone.",
    
    "IRLTLT01EZM156N": "10-year Euro Area government bond yield (weighted average). The benchmark long-term rate for the Eurozone, primarily driven by German Bunds. Key for mortgage rates and corporate borrowing.",
    
    "IRLTLT01DEM156N": "10-year German government bond yield (Bund). Considered the Eurozone's risk-free rate benchmark. Movements reflect ECB policy expectations, inflation outlook, and global safe-haven flows. The foundation for all Euro sovereign spreads.",
    
    "IRLTLT01FRM156N": "10-year French government bond yield (OAT - Obligations Assimilables du Trésor). The spread vs German Bunds reflects France's fiscal risk premium. Widening spreads signal country-specific stress or political uncertainty.",
    
    # EA_YIELD_CURVE removed - was duplicate of IRLTLT01EZM156N
    
    "BAMLHE00EHYIEY": "ICE BofA Euro High Yield Corporate Bond Index Option-Adjusted Spread. Measures credit risk premium for below-investment-grade Euro borrowers. Widens in stress, tightens when risk appetite is high.",
    
    "EUROSTAT_ESI_EA": "European Commission Economic Sentiment Indicator. Composite of business and consumer confidence surveys across sectors. Above 100 = above-trend confidence.",
    
    "EUROSTAT_CCI_EA": "European Commission Consumer Confidence Indicator. Surveys households on financial situation, economic outlook, and spending intentions. Leading indicator for consumption.",
    
    "EA_INDUSTRIAL_CONF": "Eurozone Industrial Confidence Index (balance of positive minus negative assessments). Surveys manufacturers on production expectations, order books, and stocks. Leading indicator for industrial activity.",
    
    "^STOXX50E": "Euro Stoxx 50 Index. Blue-chip benchmark covering 50 large companies across 11 Eurozone countries. Represents European corporate health, earnings expectations, and risk sentiment. Rising markets signal confidence in Eurozone recovery; falling markets often precede economic weakness or sovereign stress.",
    
    "LRHUTTTTEA156S": "Eurozone harmonized unemployment rate (% of labor force). Direct measure of labor market slack. High unemployment signals weakness; low signals tightness and potential wage pressure. From FRED (more reliable than Eurostat API).",
    
    "EA19PRINTO01IXOBM": "Euro Area Industrial Production Index (level). Measures manufacturing, mining, and utilities output. Key GDP component and cyclical indicator. Rising production signals economic expansion; falling indicates contraction. YoY growth computed from index level.",
    
    
    "NAEXKP01EZQ657S": "Real Gross Domestic Product for Euro Area (level). The headline measure of economic output across all 20 Eurozone countries. Released quarterly with a lag.",
    
    "VXEEMCLS": "CBOE Emerging Markets ETF Volatility Index. Used as a proxy for Euro risk appetite since no official Euro VIX exists. Rising volatility indicates risk-off sentiment affecting Euro assets.",
    
    "EA_HOUSE_PRICES": "Euro Area House Price Index (YoY % change). Tracks residential property prices across the Eurozone. Lags the cycle but reflects household wealth and mortgage lending conditions.",
    
    "LCEAMN01EZQ661S": "Unit Labor Costs for Euro Area. Measures labor cost per unit of output. Rising ULC signals wage inflation that can feed into consumer prices and squeeze margins.",
    
    "EA_HICP_HEADLINE": "Harmonized Index of Consumer Prices - All Items (YoY % change). The ECB's primary inflation measure. Target is 2% over the medium term.",
    
    "CP0000EZ19M086NEST": "Harmonized Index of Consumer Prices - All Items (index level). The broadest measure of Eurozone consumer price inflation, covering all goods and services in the consumption basket. Compute YoY manually from level.",
    
    "CPHPLA01EZM661N": "HICP Core ex Food & Energy (YoY % change). Strips out volatile food and energy prices to reveal underlying inflation trends. The ECB's preferred measure for assessing persistent inflation pressures. Already YoY series.",
    
    "ECBDFR": "ECB Deposit Facility Rate. The rate banks receive for depositing excess reserves with the ECB. The primary policy tool—higher rates tighten financial conditions, lower rates ease them.",
    
    # ============================================================================
    # UK NARRATIVES - REMOVED FOR V1 (Phase 2)
    # ============================================================================
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config_df() -> pd.DataFrame:
    """Return the indicator config as a DataFrame"""
    return pd.DataFrame(US_INDICATOR_CONFIG)

def get_interpretation(type_tag: str, direction: str) -> str:
    """Get interpretation text for a given type_tag and direction"""
    rules = INTERPRETATION_RULES.get(type_tag, {})
    return rules.get(direction, "Trend interpretation unavailable.")

def get_narrative(series_id: str) -> str:
    """Get the hover narrative for a given series_id"""
    return INDICATOR_NARRATIVES.get(series_id, "No description available.")

def get_fun_line(series_id: str) -> str:
    """Get the fun one-liner for a given series_id"""
    return INDICATOR_FUN_LINE.get(series_id, "An important economic indicator.")

def trend_direction(trend_label: str) -> str:
    """Map trend_label to direction bucket"""
    if "Strong up" in trend_label or "Mild up" in trend_label:
        return "up"
    if "Strong down" in trend_label or "Mild down" in trend_label:
        return "down"
    if "Flat" in trend_label:
        return "flat"
    return "unknown"

def base_phrase(direction: str, level_pct: float) -> str:
    """Generate base phrase based on direction and level percentile"""
    if pd.isna(level_pct):
        return "Signal unclear so far."
    
    high = level_pct > 60
    low  = level_pct < 40
    
    if direction == "up" and high:
        return "Rising from already elevated levels"
    if direction == "up" and low:
        return "Rising off the lows"
    if direction == "down" and high:
        return "Pulling back from elevated territory"
    if direction == "down" and low:
        return "Sliding further below trend"
    if direction == "flat":
        return "Flat overall"
    
    return "Moving, but without a strong pattern yet"

# Type-specific clauses for dynamic interpretation
TYPE_CLAUSE = {
    "inflation":          "for inflation expectations.",
    "inflation_expectation": "for inflation expectations.",
    "policy_rate":        "for the policy backdrop.",
    "real_rate":          "for real funding conditions.",
    "yield_curve_slope":  "for recession odds.",
    "credit_spread":      "for credit stress.",
    "growth_activity":    "for real growth momentum.",
    "labor_quantity":     "for hiring strength.",
    "labor_slack":        "for labor slack.",
    "wages_costs":        "for wage pressure.",
    "housing_activity":   "for the housing pulse.",
    "housing_slack":      "for housing supply.",
    "mortgage_rate":      "for housing affordability.",
    "sentiment":          "for confidence in the outlook.",
    "volatility_risk_off":"for risk appetite.",
    "lending_standards":  "for credit availability.",
    "fx_index":           "for global dollar conditions.",
    "liquidity":          "for short-term dollar liquidity.",
}

def dynamic_interpretation(trend_label: str, level_percentile: float, type_tag: str) -> str:
    """Generate dynamic one-line interpretation"""
    dir_ = trend_direction(trend_label)
    base = base_phrase(dir_, level_percentile)
    tail = TYPE_CLAUSE.get(type_tag, "")
    text = f"{base} {tail}".strip()
    return text

def trend_explainer(trend_label: str) -> str:
    """Simple explanation of trend direction"""
    if "Strong up" in trend_label or "Mild up" in trend_label:
        return "Momentum improving over the last 6 months."
    if "Strong down" in trend_label or "Mild down" in trend_label:
        return "Momentum softening over the last 6 months."
    if "Flat" in trend_label:
        return "Little net change over the last 6 months."
    return "Trend not available."

