"""
Configuration file for Nikhil Market View - Cycle Dashboard v2
Indicators with REGION dimension for US / Eurozone / Compare views
Updated: CSV sources for Eurozone indicators
"""

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Federal Reserve Economic Data (FRED) API
FRED_API_KEY = "78a98e3b4301fc8c12409c5507f13fd7"

# European Central Bank (ECB) - No API key needed for most endpoints
ECB_BASE_URL = "https://data-api.ecb.europa.eu/service/data"

# Financial Modeling Prep (FMP) API
# Get free key at: https://financialmodelingprep.com/developer/docs/
# Free tier: 250 API calls/day (enough for daily dashboard updates)
FMP_API_KEY = "HSHHWP9eNzUu8Y8OIgBgEy6D7zCbrDGa"  # Replace with your actual key

# =============================================================================
# ALL INDICATORS - US & EUROZONE
# =============================================================================

INDICATORS = {
    # ============================================================================
    # US INDICATORS
    # ============================================================================
    
    # LEADING - US
    'T10Y3M': {
        'name': '10Y-3M Yield Curve',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': '10-year minus 3-month treasury yield spread',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'BAMLH0A0HYM2': {
        'name': 'High Yield Spread',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'ICE BofA High Yield spread over Treasuries',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'BAMLC0A4CBBB': {
        'name': 'BBB Corporate Spread',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'ICE BofA BBB Corporate spread',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'HOUST': {
        'name': 'Housing Starts',
        'category': 'Housing',
        'frequency': 'monthly',
        'description': 'New privately-owned housing units started',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'T10YIEM': {
        'name': '10Y Breakeven Inflation',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': '10-year breakeven inflation rate',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'DFII10': {
        'name': '10Y Real Rate (TIPS)',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': '10-Year Treasury Inflation-Indexed Security',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'US_YIELD_CURVE': {
        'name': 'US Yield Curve (1Y–10Y)',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'The policy-vs-growth tug-of-war — where markets judge whether the Fed is too tight or too loose.',
        'indicator_type': 'Leading',
        'region': 'US',
        'source': 'derived_file',  # Pre-computed, load from file (fallback: compute on-fly)
        'spread_component_1': 'DGS10',  # 10Y Treasury
        'spread_component_2': 'DGS1',   # 1Y Treasury
        'inverted': False,  # Steepening (positive) = good, flattening/inversion = bad
        'interpretation_notes': 'Use 6-month change in spread. Steepening → easing cycle / growth optimism. Flattening or inversion → policy pressure / growth skepticism.',
        'display_unit': 'bp'  # Display as basis points
    },
    'DGS1': {
        'name': 'US 1Y Treasury',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'The Fed whisper channel — where policy expectations move first.',
        'indicator_type': 'Contextual',  # NOT scored in Leading
        'region': 'US',
        'contextual': True,  # Flag for exclusion from scoring
        'interpretation_notes': 'Policy expectations only. Does NOT contribute independently to Leading score.'
    },
    'NAPM': {
        'name': 'ISM Manufacturing PMI',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'ISM manufacturing diffusion index (>50 = expansion, <50 = contraction)',
        'indicator_type': 'Leading',
        'region': 'US',
        'use_level': True,  # Display as absolute level (around 50), NOT normalized
        'interpretation_notes': 'Diffusion index: >50 = expansion, <50 = contraction. Display level, not YoY or rebased.'
    },
    'NAPMNOI': {
        'name': 'ISM Manufacturing New Orders',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'ISM new orders diffusion index (>50 = expansion, <50 = contraction)',
        'indicator_type': 'Leading',
        'region': 'US',
        'use_level': True,  # Display as absolute level (around 50), NOT normalized
        'interpretation_notes': 'Diffusion index: >50 = expansion, <50 = contraction. Display level, not YoY or rebased.'
    },
    'AWHMAN': {
        'name': 'Avg Weekly Hours - Manufacturing',
        'category': 'Labor',
        'frequency': 'monthly',
        'description': 'Hours usually roll over before payrolls',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'UMCSENT': {
        'name': 'Consumer Sentiment (U of M)',
        'category': 'Sentiment',
        'frequency': 'monthly',
        'description': 'Classic lead on consumption (1966:Q1=100)',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'DRTSCILM': {
        'name': 'Bank Lending Standards',
        'category': 'Credit',
        'frequency': 'quarterly',
        'description': 'Net % of banks tightening credit standards',
        'indicator_type': 'Leading',
        'inverted': True,
        'region': 'US'
    },
    'MSACSR': {
        'name': 'Months Supply New Houses',
        'category': 'Housing',
        'frequency': 'monthly',
        'description': 'Housing inventory in months',
        'indicator_type': 'Leading',
        'region': 'US'
    },
    'VIXCLS': {
        'name': 'VIX (Equity Volatility)',
        'category': 'Financial Conditions',
        'frequency': 'daily',
        'description': 'Market stress gauge — not a growth signal',
        'indicator_type': 'Leading',
        'inverted': True,
        'region': 'US'
    },
    'SP500': {
        'name': 'S&P 500 (YoY %)',
        'category': 'Financial Conditions',
        'frequency': 'daily',
        'description': 'Risk appetite indicator (YoY change) — NOT real growth',
        'indicator_type': 'Contextual',  # Removed from Leading scoring
        'region': 'US',
        'source': 'fred',
        'use_yoy': True,  # YoY % change, not level
        'contextual': True,  # Exclude from Leading score
        'interpretation_notes': 'Strong equities + weak growth = late-cycle or liquidity-driven rally'
    },
    'NASDAQCOM': {
        'name': 'NASDAQ (YoY %)',
        'category': 'Financial Conditions',
        'frequency': 'daily',
        'description': 'Tech risk appetite (YoY change) — NOT real growth',
        'indicator_type': 'Contextual',  # Removed from Leading scoring
        'region': 'US',
        'source': 'fred',
        'use_yoy': True,  # YoY % change, not level
        'contextual': True,  # Exclude from Leading score
        'interpretation_notes': 'Strong equities + weak growth = late-cycle or liquidity-driven rally'
    },
    
    # COINCIDENT - US
    'DGS10': {
        'name': 'US 10Y Treasury',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'Ten-year Treasury constant maturity rate (macro state)',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    'PAYEMS': {
        'name': 'Nonfarm Payrolls',
        'category': 'Labor',
        'frequency': 'monthly',
        'description': 'Monthly job additions (thousands)',
        'indicator_type': 'Coincident',
        'use_monthly_change': True,
        'region': 'US'
    },
    'INDPRO': {
        'name': 'Industrial Production',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'Industrial production index',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    'RSXFS': {
        'name': 'Retail Sales',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'Advance retail sales',
        'indicator_type': 'Coincident',
        'use_yoy': True,
        'region': 'US'
    },
    'PCECC96': {
        'name': 'Real Personal Consumption',
        'category': 'Growth',
        'frequency': 'quarterly',
        'description': 'Real PCE in billions of chained 2017 USD (SAAR)',
        'indicator_type': 'Coincident',
        'use_yoy': True,
        'region': 'US'
    },
    'DFF': {
        'name': 'Federal Funds Rate',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'Effective federal funds rate',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    'SOFR': {
        'name': 'SOFR',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'Secured Overnight Financing Rate',
        'indicator_type': 'Coincident',
        'backfill_series': 'DFF',
        'region': 'US'
    },
    'MORTGAGE30US': {
        'name': '30Y Mortgage Rate',
        'category': 'Housing',
        'frequency': 'weekly',
        'description': '30-year fixed rate mortgage average',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    'RRPONTSYD': {
        'name': 'Reverse Repo',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'Overnight reverse repurchase agreements',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    'DTWEXBGS': {
        'name': 'Dollar Index',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'Trade Weighted US Dollar Index',
        'indicator_type': 'Coincident',
        'region': 'US'
    },
    
    # LAGGING - US
    'UNRATE': {
        'name': 'Unemployment Rate',
        'category': 'Labor',
        'frequency': 'monthly',
        'description': 'Civilian unemployment rate',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    'CPIAUCSL': {
        'name': 'CPI All Items',
        'category': 'Inflation',
        'frequency': 'monthly',
        'description': 'Consumer Price Index - All Urban Consumers',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    'CPILFESL': {
        'name': 'Core CPI',
        'category': 'Inflation',
        'frequency': 'monthly',
        'description': 'CPI excluding food and energy',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    'PCEPI': {
        'name': 'PCE Price Index',
        'category': 'Inflation',
        'frequency': 'monthly',
        'description': 'Personal consumption expenditures price index',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    'PCEPILFE': {
        'name': 'Core PCE',
        'category': 'Inflation',
        'frequency': 'monthly',
        'description': 'PCE excluding food and energy (Fed preferred measure)',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    'ECIWAG': {
        'name': 'Employment Cost Index',
        'category': 'Labor',
        'frequency': 'quarterly',
        'description': 'Employment Cost Index - Wages and Salaries',
        'indicator_type': 'Lagging',
        'region': 'US'
    },
    # 'TEDRATE': {
    #     'name': 'TED Spread',
    #     'category': 'Fixed Income',
    #     'frequency': 'daily',
    #     'description': '3-month LIBOR minus 3-month T-bill rate (DISCONTINUED - LIBOR ended 2022)',
    #     'indicator_type': 'Lagging',
    #     'region': 'US'
    # },
    
    # ============================================================================
    # EUROZONE INDICATORS - Hybrid Stack (FRED + Eurostat)
    # ============================================================================
    # 
    # Data Sources:
    # - FRED: Rates, credit spreads, inflation (via Eurostat republished)
    # - Eurostat v2: Sentiment surveys, unemployment
    # - Eurostat legacy: GDP
    #
    # NOTE: Germany/France drill-down disabled per user request.
    # NOTE: Industrial Production & Retail not available with fresh data (<6mo).
    # ============================================================================
    
    # LEADING - Eurozone (7 indicators)
    # ---------------------------------
    # Rates & Curves (German Bunds as Euro proxy via FMP)
    'IRSTCI01EZM156N': {
        'name': 'Euro 1Y Yield',
        'category': 'Fixed Income',
        'frequency': 'monthly',
        'description': 'The ECB whisper channel — where policy expectations move first.',
        'indicator_type': 'Contextual',  # NOT scored in Leading
        'region': 'Eurozone',
        'source': 'fred',
        'contextual': True,  # Flag for exclusion from scoring
        'interpretation_notes': 'Policy expectations only. Does NOT contribute independently to Leading score.'
    },
    'IRLTLT01EZM156N': {
        'name': 'Euro 10Y Yield',
        'category': 'Fixed Income',
        'frequency': 'monthly',
        'description': "The market's long-run verdict on Eurozone growth and inflation.",
        'indicator_type': 'Coincident',  # MOVED from Leading to Coincident
        'region': 'Eurozone',
        'source': 'fred',
        'interpretation_notes': 'Macro state / long-run conditions. Does NOT contribute to Leading score.'
    },
    # NEW: Euro Yield Curve (10Y - 1Y spread) - PRIMARY rates signal for Leading
    'EU_YIELD_CURVE': {
        'name': 'Euro Yield Curve (1Y–10Y)',
        'category': 'Fixed Income',
        'frequency': 'monthly',
        'description': 'The policy-vs-growth tug-of-war — where markets judge whether the ECB is too tight or too loose.',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'derived_file',  # Pre-computed, load from file (fallback: compute on-fly)
        'spread_component_1': 'IRLTLT01EZM156N',  # EA 10Y
        'spread_component_2': 'IRSTCI01EZM156N',  # EA 1Y
        'inverted': False,  # Steepening (positive) = good, flattening/inversion = bad
        'interpretation_notes': 'Use 6-month change in spread. Steepening → easing cycle / growth optimism. Flattening or inversion → policy pressure / growth skepticism.',
        'display_unit': 'bp'  # Display as basis points
    },
    'IRLTLT01DEM156N': {
        'name': 'German 10Y Bund',
        'category': 'Fixed Income',
        'frequency': 'monthly',
        'description': '10-year German government bond yield (Bund)',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'fred'
    },
    'IRLTLT01FRM156N': {
        'name': 'French 10Y OAT',
        'category': 'Fixed Income',
        'frequency': 'monthly',
        'description': '10-year French government bond yield (OAT) - used for spread calculation',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'fred',
        'hidden': True  # Don't display separately, only for FR_DE_SPREAD
    },
    'FR_DE_SPREAD': {
        'name': 'France-Germany 10Y Spread',
        'category': 'Credit',
        'frequency': 'monthly',
        'description': 'French OAT vs German Bund 10Y spread (sovereign risk premium)',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'derived_file',  # Pre-computed, load from file (fallback: compute on-fly)
        'spread_component_1': 'IRLTLT01FRM156N',  # FR 10Y
        'spread_component_2': 'IRLTLT01DEM156N',  # DE 10Y
        'inverted': True  # Higher spread = more stress
    },
    # Full Yield Curve (CSV - ECB)
    # Removed EA_YIELD_CURVE - duplicate of IRLTLT01EZM156N (10Y Euro Yield)
    # Credit Spreads
    'BAMLHE00EHYIEY': {
        'name': 'Euro HY Corporate Spread',
        'category': 'Fixed Income',
        'frequency': 'daily',
        'description': 'ICE BofA Euro High Yield OAS',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'fred'
    },
    # Sentiment (Eurostat)
    'EUROSTAT_ESI_EA': {
        'name': 'Economic Sentiment Index (EUR)',
        'category': 'Sentiment',
        'frequency': 'monthly',
        'description': "The Eurozone's mood ring — business and consumer confidence in one number.",
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_industrial_confidence_ea20.csv',
        'interpretation_notes': 'Downtrends precede investment slowdowns. Stabilization after declines often marks late-cycle pauses, not recoveries.'
    },
    'EUROSTAT_CCI_EA': {
        'name': 'Consumer Confidence (EUR)',
        'category': 'Sentiment',
        'frequency': 'monthly',
        'description': 'The household gut check — whether consumers are bracing or spending.',
        'indicator_type': 'Leading',
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_industrial_confidence_ea20.csv',
        'interpretation_notes': 'Level matters less than direction. Sustained weakness = demand risk. Sharp drops = early recession signal.'
    },
    
    
    # COINCIDENT - Eurozone (6 indicators)
    # -------------------------------------
    # Labor - EUROSTAT DIRECT
    'EA_UNEMPLOYMENT': {
        'name': 'Unemployment Rate (EUR)',
        'category': 'Labor',
        'frequency': 'monthly',
        'description': 'Euro Area harmonized unemployment rate (Eurostat)',
        'indicator_type': 'Coincident',
        'inverted': True,
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_unemployment_ea20.csv',
        'eurostat_filters': {'s_adj': 'SA', 'age': 'TOTAL', 'sex': 'T', 'unit': 'PC_ACT'},
        'use_yoy': False
    },
    'EA_EMPLOYMENT_RATE': {
        'name': 'Employment Rate (EUR)',
        'category': 'Labor',
        'frequency': 'quarterly',
        'description': 'Euro Area employment rate (% of population 15-64, Eurostat)',
        'indicator_type': 'Coincident',
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_employment_ea20.csv',
        'use_yoy': False
    },
    # Growth - Use Germany (more reliable data)
    'DEUPRO': {
        'name': 'Industrial Production (Germany)',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'German industrial production index',
        'indicator_type': 'Coincident',
        'region': 'Eurozone',
        'source': 'fred',
        'use_yoy': True,  # Index - use YoY
        'use_mom': False
    },
    'EA19RETTOT01IXOBM': {
        'name': 'Retail Sales Volume (EUR)',
        'category': 'Growth',
        'frequency': 'monthly',
        'description': 'Euro Area retail trade volume index',
        'indicator_type': 'Coincident',
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_retail_ea20.csv',
        'use_yoy': True,  # Index - use YoY
        'use_mom': False
    },
    'CLVMNACSCAB1GQEA19': {
        'name': 'Euro Area Real GDP',
        'category': 'Growth',
        'frequency': 'quarterly',
        'description': 'Real GDP for Euro Area (YoY growth)',
        'indicator_type': 'Coincident',
        'use_yoy': True,  # Level series - compute YoY %
        'use_mom': False,
        'region': 'Eurozone',
        'source': 'fred'
    },
    # Market Vol (proxy)
    'VXEEMCLS': {
        'name': 'EM Vol Index',
        'category': 'Financial Conditions',
        'frequency': 'daily',
        'description': 'CBOE EM ETF Volatility (Euro risk proxy) — not a growth signal',
        'indicator_type': 'Coincident',
        'inverted': True,
        'region': 'Eurozone',
        'source': 'fred'
    },
    
    # LAGGING - Eurozone (3 indicators)
    # ----------------------------------
    # Inflation
    'CP0000EZ19M086NEST': {
        'name': 'HICP All Items (EUR)',
        'category': 'Inflation',
        'frequency': 'monthly',
        'description': 'Harmonized Index of Consumer Prices - All Items',
        'indicator_type': 'Lagging',
        'use_yoy': True,  # Show as YoY % inflation, not index level
        'region': 'Eurozone',
        'source': 'fred'
    },
    # Wages - EUROSTAT DIRECT (Index - compute YoY)
    'EA_WAGE_GROWTH': {
        'name': 'Labor Cost Index (EUR)',
        'category': 'Labor',
        'frequency': 'quarterly',
        'description': 'Euro Area labor cost index - hourly costs (Eurostat)',
        'indicator_type': 'Lagging',
        'region': 'Eurozone',
        'source': 'csv',
        'csv_file': 'eurozone_data/eurostat_ulc_ea20.csv',
        'use_yoy': True,  # Index - use YoY for percentile/trend
        'use_mom': False
    },
    # Policy Rate
    'ECBDFR': {
        'name': 'ECB Deposit Rate',
        'category': 'Fixed Income',
        'frequency': 'irregular',
        'description': 'ECB deposit facility rate',
        'indicator_type': 'Lagging',
        'region': 'Eurozone',
        'source': 'fred',
        'use_yoy': False
    },
    
    # =========================================================================
    # UK INDICATORS - REMOVED (Phase 2)
    # UK data quality on FRED is poor. Requires ONS + BoE API integration.
    # =========================================================================
    
    }

# Backward compatibility - keep old variable names
US_INDICATORS = {k: v for k, v in INDICATORS.items() if v.get('region') == 'US'}
EUROPEAN_INDICATORS = {k: v for k, v in INDICATORS.items() if v.get('region') == 'Eurozone'}
JAPAN_INDICATORS = {k: v for k, v in INDICATORS.items() if v.get('region') == 'Japan'}

# =============================================================================
# ANALYSIS SETTINGS
# =============================================================================

# How many years of historical data to fetch
LOOKBACK_YEARS = 20

# Recent regime comparison period (years)
RECENT_YEARS = 5

# Frequency-aware freshness thresholds (in months)
FRESHNESS_THRESHOLDS = {
    'daily': 3,      # Daily data: 3 months
    'weekly': 4,     # Weekly data: 4 months
    'monthly': 6,    # Monthly data: 6 months
    'quarterly': 9,  # Quarterly data: 9 months (allows for 2Q lag)
    'annual': 18,    # Annual data: 18 months
    'irregular': 12  # Irregular: 12 months
}

# Percentile thresholds for commentary
EXTREME_HIGH = 90
HIGH = 75
LOW = 25
EXTREME_LOW = 10

# Momentum thresholds (for 3-month change)
STRONG_UP = 5.0
MILD_UP = 1.0
MILD_DOWN = -1.0
STRONG_DOWN = -5.0

# Visualization settings
CHART_STYLE = 'seaborn-v0_8-darkgrid'
FIGURE_DPI = 300
COLOR_SCHEME = {
    'extreme_high': '#d32f2f',  # Red
    'high': '#f57c00',          # Orange
    'neutral': '#7cb342',       # Green
    'low': '#0288d1',           # Blue
    'extreme_low': '#512da8',   # Purple
}

# Summary box colors
SUMMARY_COLORS = {
    'weak': '#d32f2f',      # Red
    'neutral': '#FFA500',   # Orange
    'strong': '#7cb342',    # Green
}

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

OUTPUT_DIR = '.'
SAVE_CSV = True
SAVE_JSON = True

