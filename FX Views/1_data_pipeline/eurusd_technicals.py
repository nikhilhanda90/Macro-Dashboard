"""
EURUSD Technical Analysis
Pure price-based indicators with scoring and narrative generation
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
from pathlib import Path

def fetch_eurusd_daily(lookback_days=730):
    """Fetch daily EURUSD data from Yahoo Finance"""
    ticker = yf.Ticker("EURUSD=X")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    df = ticker.history(start=start_date, end=end_date, interval='1d')
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.index = pd.to_datetime(df.index)
    
    return df

def calculate_indicators(df):
    """Calculate all technical indicators"""
    data = df.copy()
    
    # Moving Averages
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_100'] = data['Close'].rolling(window=100).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    
    # RSI (14)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD (12, 26, 9)
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
    
    # Bollinger Bands (20, 2)
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    bb_std = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
    data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
    data['BB_Width'] = data['BB_Upper'] - data['BB_Lower']
    
    # ATR (20)
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    data['ATR'] = true_range.rolling(14).mean()
    
    # 1-year high/low
    data['Year_High'] = data['High'].rolling(window=252).max()
    data['Year_Low'] = data['Low'].rolling(window=252).min()
    
    return data

def calculate_fibonacci_levels(df, lookback_months=15):
    """Calculate Fibonacci retracement levels from last major swing"""
    lookback_days = lookback_months * 21
    recent_data = df.tail(lookback_days)
    
    swing_high = recent_data['High'].max()
    swing_low = recent_data['Low'].min()
    diff = swing_high - swing_low
    
    fib_levels = {
        '0.0': swing_low,
        '23.6': swing_low + 0.236 * diff,
        '38.2': swing_low + 0.382 * diff,
        '50.0': swing_low + 0.500 * diff,
        '61.8': swing_low + 0.618 * diff,
        '100.0': swing_high
    }
    
    return fib_levels

def calculate_percentiles(df):
    """Calculate 5-year percentiles for volatility metrics"""
    lookback_5y = min(len(df), 252 * 5)
    
    percentiles = {}
    
    # BB Width percentile
    if 'BB_Width' in df.columns:
        bb_width_5y = df['BB_Width'].tail(lookback_5y)
        current_bb_width = df['BB_Width'].iloc[-1]
        percentiles['bb_width_pct'] = (bb_width_5y < current_bb_width).sum() / len(bb_width_5y) * 100
    
    # ATR percentile
    if 'ATR' in df.columns:
        atr_5y = df['ATR'].tail(lookback_5y)
        current_atr = df['ATR'].iloc[-1]
        percentiles['atr_pct'] = (atr_5y < current_atr).sum() / len(atr_5y) * 100
    
    return percentiles

def calculate_technical_score(latest, fib_levels, percentiles):
    """Calculate technical score (-3 to +3)"""
    score = 0.0
    
    spot = latest['Close']
    
    # === STRUCTURE SCORE (50%) ===
    # 200-day MA
    if pd.notna(latest['SMA_200']):
        score += 1.0 if spot > latest['SMA_200'] else -1.0
    
    # 100-day MA
    if pd.notna(latest['SMA_100']):
        score += 0.5 if spot > latest['SMA_100'] else -0.5
    
    # 50-day MA
    if pd.notna(latest['SMA_50']):
        score += 0.5 if spot > latest['SMA_50'] else -0.5
    
    # Fib 50%
    fib_50 = fib_levels.get('50.0')
    if fib_50:
        score += 0.5 if spot > fib_50 else -0.5
    
    # === MOMENTUM & VOLATILITY SCORE (50%) ===
    # RSI
    if pd.notna(latest['RSI']):
        if latest['RSI'] > 55:
            score += 1.0
        elif latest['RSI'] < 45:
            score -= 1.0
    
    # MACD (rising/falling based on histogram)
    if pd.notna(latest['MACD_Hist']):
        # Compare to previous value
        if 'MACD_Hist_prev' in latest:
            if latest['MACD_Hist'] > latest['MACD_Hist_prev']:
                score += 1.0
            else:
                score -= 1.0
    
    # Bollinger
    bb_width_pct = percentiles.get('bb_width_pct', 50)
    if bb_width_pct < 30:
        # Compressed - neutral
        pass
    elif bb_width_pct > 70:
        # Expanded
        if spot > latest['BB_Middle']:
            score += 0.5  # expansion up
        else:
            score -= 0.5  # expansion down
    
    # ATR
    atr_pct = percentiles.get('atr_pct', 50)
    if atr_pct > 70:
        score -= 0.5  # exhaustion risk
    
    # Clamp to -3 to +3
    score = max(-3.0, min(3.0, score))
    
    return score

def determine_regime(score):
    """Determine technical regime from score"""
    if score >= 1.5:
        return "Bullish"
    elif score <= -1.5:
        return "Bearish"
    else:
        return "Neutral"

def get_key_levels(latest, fib_levels):
    """Get top 5 key levels with distances"""
    spot = latest['Close']
    
    levels = []
    
    # 200-day MA
    if pd.notna(latest['SMA_200']):
        levels.append({
            'name': '200-day MA',
            'price': latest['SMA_200'],
            'distance_pct': ((latest['SMA_200'] - spot) / spot) * 100,
            'type': 'Support' if latest['SMA_200'] < spot else 'Resistance'
        })
    
    # Fib levels (38.2, 50, 61.8)
    for fib_name in ['38.2', '50.0', '61.8']:
        if fib_name in fib_levels:
            fib_price = fib_levels[fib_name]
            levels.append({
                'name': f'Fib {fib_name}%',
                'price': fib_price,
                'distance_pct': ((fib_price - spot) / spot) * 100,
                'type': 'Support' if fib_price < spot else 'Resistance'
            })
    
    # 100-day MA
    if pd.notna(latest['SMA_100']):
        levels.append({
            'name': '100-day MA',
            'price': latest['SMA_100'],
            'distance_pct': ((latest['SMA_100'] - spot) / spot) * 100,
            'type': 'Support' if latest['SMA_100'] < spot else 'Resistance'
        })
    
    # 1-year high/low (closest)
    year_high_dist = abs(((latest['Year_High'] - spot) / spot) * 100)
    year_low_dist = abs(((latest['Year_Low'] - spot) / spot) * 100)
    
    if year_high_dist < year_low_dist:
        levels.append({
            'name': '1-year High',
            'price': latest['Year_High'],
            'distance_pct': ((latest['Year_High'] - spot) / spot) * 100,
            'type': 'Resistance'
        })
    else:
        levels.append({
            'name': '1-year Low',
            'price': latest['Year_Low'],
            'distance_pct': ((latest['Year_Low'] - spot) / spot) * 100,
            'type': 'Support'
        })
    
    # 50-day MA
    if pd.notna(latest['SMA_50']):
        levels.append({
            'name': '50-day MA',
            'price': latest['SMA_50'],
            'distance_pct': ((latest['SMA_50'] - spot) / spot) * 100,
            'type': 'Support' if latest['SMA_50'] < spot else 'Resistance'
        })
    
    # Sort by absolute distance and take top 5
    levels.sort(key=lambda x: abs(x['distance_pct']))
    return levels[:5]

def generate_narrative(latest, score, regime, fib_levels, percentiles):
    """Generate technical narrative paragraph"""
    spot = latest['Close']
    
    # Price vs 200d MA
    if pd.notna(latest['SMA_200']):
        if spot > latest['SMA_200']:
            ma_context = f"continues to trade above its 200-day moving average ({latest['SMA_200']:.4f})"
        else:
            ma_context = f"remains below its 200-day moving average ({latest['SMA_200']:.4f}), with repeated rejections near resistance"
    else:
        ma_context = "shows mixed trend structure"
    
    # Momentum
    rsi = latest['RSI']
    if rsi > 70:
        momentum = "overbought conditions"
    elif rsi < 30:
        momentum = "oversold conditions"
    elif rsi > 55:
        momentum = "bullish momentum"
    elif rsi < 45:
        momentum = "bearish momentum"
    else:
        momentum = "neutral momentum"
    
    # Volatility
    bb_width_pct = percentiles.get('bb_width_pct', 50)
    if bb_width_pct < 30:
        vol_state = "volatility compressed, suggesting a directional move is likely but not yet confirmed"
    elif bb_width_pct > 70:
        vol_state = "volatility elevated, indicating an active trend"
    else:
        vol_state = "volatility normal"
    
    # Net stance
    if regime == "Bullish":
        stance = "Net technical stance: constructive"
    elif regime == "Bearish":
        stance = "Net technical stance: defensive"
    else:
        stance = "Net technical stance: neutral / range-bound"
    
    narrative = f"EURUSD {ma_context}. {momentum.capitalize()} and {vol_state}. {stance}."
    
    return narrative

def run_technical_analysis():
    """Main function to run technical analysis"""
    print("="*80)
    print("EURUSD TECHNICAL ANALYSIS")
    print("="*80)
    
    # Fetch data
    print("\nFetching daily EURUSD data...")
    df = fetch_eurusd_daily(lookback_days=730)
    print(f"✓ {len(df)} days loaded")
    
    # Calculate indicators
    print("\nCalculating technical indicators...")
    df = calculate_indicators(df)
    print("✓ Indicators calculated")
    
    # Fibonacci levels
    print("\nCalculating Fibonacci levels...")
    fib_levels = calculate_fibonacci_levels(df, lookback_months=15)
    print(f"✓ Fib levels: {', '.join([f'{k}: {v:.4f}' for k, v in fib_levels.items()])}")
    
    # Percentiles
    print("\nCalculating volatility percentiles...")
    percentiles = calculate_percentiles(df)
    print(f"✓ BB Width: {percentiles.get('bb_width_pct', 0):.1f}%ile, ATR: {percentiles.get('atr_pct', 0):.1f}%ile")
    
    # Get latest
    latest = df.iloc[-1].copy()
    latest['MACD_Hist_prev'] = df.iloc[-2]['MACD_Hist']
    
    # Calculate score
    print("\nCalculating technical score...")
    score = calculate_technical_score(latest, fib_levels, percentiles)
    regime = determine_regime(score)
    print(f"✓ Technical Score: {score:+.2f} ({regime})")
    
    # Key levels
    print("\nIdentifying key levels...")
    key_levels = get_key_levels(latest, fib_levels)
    print("✓ Top 5 levels:")
    for level in key_levels:
        print(f"  {level['name']}: {level['price']:.4f} ({level['distance_pct']:+.2f}%) - {level['type']}")
    
    # Generate narrative
    print("\nGenerating technical narrative...")
    narrative = generate_narrative(latest, score, regime, fib_levels, percentiles)
    print(f"✓ {narrative}")
    
    # Save outputs
    output_dir = Path(__file__).parent.parent / 'technical_outputs'
    output_dir.mkdir(exist_ok=True)
    
    # Save full data
    df.to_csv(output_dir / 'eurusd_technical_data.csv')
    
    # Save summary
    summary = {
        'date': latest.name.strftime('%Y-%m-%d'),
        'spot': float(latest['Close']),
        'technical_score': float(score),
        'regime': regime,
        'narrative': narrative,
        'indicators': {
            'SMA_50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else None,
            'SMA_100': float(latest['SMA_100']) if pd.notna(latest['SMA_100']) else None,
            'SMA_200': float(latest['SMA_200']) if pd.notna(latest['SMA_200']) else None,
            'RSI': float(latest['RSI']) if pd.notna(latest['RSI']) else None,
            'MACD': float(latest['MACD']) if pd.notna(latest['MACD']) else None,
            'MACD_Signal': float(latest['MACD_Signal']) if pd.notna(latest['MACD_Signal']) else None,
            'BB_Upper': float(latest['BB_Upper']) if pd.notna(latest['BB_Upper']) else None,
            'BB_Middle': float(latest['BB_Middle']) if pd.notna(latest['BB_Middle']) else None,
            'BB_Lower': float(latest['BB_Lower']) if pd.notna(latest['BB_Lower']) else None,
            'ATR': float(latest['ATR']) if pd.notna(latest['ATR']) else None,
        },
        'fib_levels': {k: float(v) for k, v in fib_levels.items()},
        'percentiles': percentiles,
        'key_levels': key_levels,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(output_dir / 'eurusd_technical_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Saved: {output_dir / 'eurusd_technical_data.csv'}")
    print(f"✓ Saved: {output_dir / 'eurusd_technical_summary.json'}")
    
    print("\n" + "="*80)
    print("TECHNICAL ANALYSIS COMPLETE")
    print("="*80)
    
    return df, summary

if __name__ == '__main__':
    run_technical_analysis()

