"""
CFTC Positioning Data - EUR FX Futures (Simplified)
Using direct CSV download from CFTC
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

def fetch_cftc_data_direct():
    """
    Fetch CFTC data directly from their website
    Using the Disaggregated Futures report which has better data structure
    """
    print("="*80)
    print("FETCHING CFTC EUR POSITIONING DATA")
    print("="*80)
    
    # Try multiple years and combine
    base_url = "https://www.cftc.gov/files/dea/history"
    
    all_data = []
    
    # Try years from 2020-2025
    for year in range(2020, 2026):
        try:
            # Financial Futures - Disaggregated format (better for EUR)
            url = f"{base_url}/dea_fut_txt_{year}.zip"
            print(f"\nTrying {year} (Disaggregated)...")
            df_year = pd.read_csv(url, compression='zip', low_memory=False)
            
            # Filter for EURO
            euro_mask = df_year['Market_and_Exchange_Names'].str.contains('EURO', case=False, na=False)
            df_euro_year = df_year[euro_mask]
            
            if not df_euro_year.empty:
                all_data.append(df_euro_year)
                print(f"  ✓ {len(df_euro_year)} EUR records")
            else:
                print(f"  ✗ No EUR data")
        
        except Exception as e:
            print(f"  ✗ Failed: {str(e)[:100]}")
            
            # Try Legacy format as backup
            try:
                url_legacy = f"{base_url}/fut_fin_txt_{year}.zip"
                print(f"  Trying Legacy format...")
                df_year = pd.read_csv(url_legacy, compression='zip', low_memory=False)
                
                euro_mask = df_year['Market_and_Exchange_Names'].str.contains('EURO', case=False, na=False)
                df_euro_year = df_year[euro_mask]
                
                if not df_euro_year.empty:
                    all_data.append(df_euro_year)
                    print(f"  ✓ {len(df_euro_year)} EUR records (Legacy)")
            except Exception as e2:
                print(f"  ✗ Legacy also failed: {str(e2)[:100]}")
                continue
    
    if not all_data:
        raise ValueError("Could not fetch any CFTC data")
    
    df_combined = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Total records: {len(df_combined)}")
    
    return df_combined

def process_positioning(df_raw):
    """Process CFTC data to get Non-Commercial positioning"""
    
    df = df_raw.copy()
    
    # Parse date
    df['date'] = pd.to_datetime(df['Report_Date_as_YYYY-MM-DD'])
    
    # Try to get Non-Commercial positions (speculators)
    # Column names vary by report type
    long_cols = [c for c in df.columns if 'NonComm' in c and 'Long' in c and 'All' in c]
    short_cols = [c for c in df.columns if 'NonComm' in c and 'Short' in c and 'All' in c]
    
    if not long_cols or not short_cols:
        print("Available columns:", df.columns.tolist())
        raise ValueError("Could not find Non-Commercial position columns")
    
    long_col = long_cols[0]
    short_col = short_cols[0]
    
    print(f"\nUsing columns:")
    print(f"  Long: {long_col}")
    print(f"  Short: {short_col}")
    
    df['long'] = pd.to_numeric(df[long_col], errors='coerce')
    df['short'] = pd.to_numeric(df[short_col], errors='coerce')
    df['net_position'] = df['long'] - df['short']
    
    # Sort and clean
    df = df.sort_values('date').reset_index(drop=True)
    df_clean = df[['date', 'long', 'short', 'net_position']].dropna()
    
    # Remove duplicates (keep most recent for each date)
    df_clean = df_clean.drop_duplicates(subset=['date'], keep='last')
    
    print(f"\n✓ Clean records: {len(df_clean)}")
    print(f"  Date range: {df_clean['date'].min()} to {df_clean['date'].max()}")
    
    # Calculate statistics
    # 6-month window (~26 weeks)
    df_clean['mean_6m'] = df_clean['net_position'].rolling(window=26, min_periods=20).mean()
    df_clean['std_6m'] = df_clean['net_position'].rolling(window=26, min_periods=20).std()
    df_clean['z_6m'] = (df_clean['net_position'] - df_clean['mean_6m']) / df_clean['std_6m']
    
    # 1-year window (~52 weeks)
    df_clean['mean_1y'] = df_clean['net_position'].rolling(window=52, min_periods=40).mean()
    df_clean['std_1y'] = df_clean['net_position'].rolling(window=52, min_periods=40).std()
    df_clean['z_1y'] = (df_clean['net_position'] - df_clean['mean_1y']) / df_clean['std_1y']
    
    # Historical percentile
    df_clean['percentile'] = df_clean['net_position'].rank(pct=True) * 100
    
    # Classification
    def classify(row):
        z = row['z_1y']
        pct = row['percentile']
        
        if pd.isna(z) or pd.isna(pct):
            return "Unknown"
        elif z > 1.5 or pct > 85:
            return "Crowded Long"
        elif z < -1.5 or pct < 15:
            return "Crowded Short"
        else:
            return "Neutral"
    
    df_clean['positioning_state'] = df_clean.apply(classify, axis=1)
    
    return df_clean

def generate_commentary(state):
    """Generate institutional commentary - NO directional predictions"""
    if state == "Crowded Long":
        return "Positioning is crowded long, historically increasing downside asymmetry and sensitivity to negative macro or policy surprises."
    elif state == "Crowded Short":
        return "Positioning is crowded short, increasing squeeze risk if macro or policy dynamics turn supportive."
    else:
        return "Positioning is neutral, suggesting limited crowding-related asymmetry."

if __name__ == '__main__':
    try:
        # Fetch data
        df_raw = fetch_cftc_data_direct()
        
        # Process
        print("\n" + "="*80)
        print("PROCESSING POSITIONING METRICS")
        print("="*80)
        df_processed = process_positioning(df_raw)
        
        # Get latest
        latest = df_processed.iloc[-1]
        commentary = generate_commentary(latest['positioning_state'])
        
        # Create summary
        summary = {
            'date': latest['date'].strftime('%Y-%m-%d'),
            'net_position': int(latest['net_position']),
            'long': int(latest['long']),
            'short': int(latest['short']),
            'z_6m': float(latest['z_6m']),
            'z_1y': float(latest['z_1y']),
            'percentile': float(latest['percentile']),
            'positioning_state': latest['positioning_state'],
            'commentary': commentary,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save
        output_dir = Path(__file__).parent.parent / 'cftc_outputs'
        output_dir.mkdir(exist_ok=True)
        
        csv_path = output_dir / 'cftc_eur_positioning.csv'
        json_path = output_dir / 'cftc_positioning_summary.json'
        
        df_processed.to_csv(csv_path, index=False)
        
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✓ Saved: {csv_path}")
        print(f"✓ Saved: {json_path}")
        
        # Display latest
        print("\n" + "="*80)
        print("LATEST EUR POSITIONING")
        print("="*80)
        print(f"Date: {summary['date']}")
        print(f"Net Position: {summary['net_position']:,} contracts")
        print(f"  Long: {summary['long']:,}")
        print(f"  Short: {summary['short']:,}")
        print(f"\nZ-Score (6m): {summary['z_6m']:+.2f}σ")
        print(f"Z-Score (1y): {summary['z_1y']:+.2f}σ")
        print(f"Percentile: {summary['percentile']:.1f}%")
        print(f"\nState: {summary['positioning_state']}")
        print(f"\nCommentary:")
        print(f"  {summary['commentary']}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

