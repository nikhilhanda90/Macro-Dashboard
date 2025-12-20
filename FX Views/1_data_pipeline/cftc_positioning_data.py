"""
CFTC Positioning Data - EUR FX Futures
Fetch and process Non-Commercial speculative positioning
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import requests
from io import BytesIO
from zipfile import ZipFile

def fetch_cftc_data(years=None):
    """
    Fetch CFTC Commitments of Traders data for EUR FX futures
    
    Parameters:
    - years: list of years to fetch (defaults to last 5 years)
    
    Returns:
    - DataFrame with EUR positioning history
    """
    if years is None:
        current_year = datetime.now().year
        years = list(range(current_year - 4, current_year + 1))
    
    all_data = []
    
    for year in years:
        try:
            # CFTC publishes financial futures data as annual zip files
            url = f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip"
            print(f"Fetching {year}...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract CSV from zip
            with ZipFile(BytesIO(response.content)) as zf:
                # List all files in zip to find the right one
                file_list = zf.namelist()
                
                # Try common naming patterns
                possible_names = [
                    f"FinFutYY{str(year)[-2:]}.txt",
                    f"annual.txt",
                    f"f_year.txt",
                    # CFTC uses 'annual.txt' for current year historical data
                ]
                
                csv_name = None
                for name in possible_names:
                    if name in file_list:
                        csv_name = name
                        break
                
                # If still not found, use first .txt file
                if csv_name is None:
                    txt_files = [f for f in file_list if f.endswith('.txt')]
                    if txt_files:
                        csv_name = txt_files[0]
                    else:
                        raise ValueError(f"No .txt file found in zip. Files: {file_list}")
                
                with zf.open(csv_name) as f:
                    df_year = pd.read_csv(f)
                    all_data.append(df_year)
            
            print(f"  ✓ {len(df_year)} records")
            
        except Exception as e:
            print(f"  ✗ Failed to fetch {year}: {e}")
            continue
    
    if not all_data:
        raise ValueError("No CFTC data fetched")
    
    # Combine all years
    df = pd.concat(all_data, ignore_index=True)
    
    # Filter for EUR FX
    euro_mask = df['Market_and_Exchange_Names'].str.contains('EURO FX', case=False, na=False)
    df_euro = df[euro_mask].copy()
    
    if df_euro.empty:
        raise ValueError("No EUR FX data found in CFTC reports")
    
    print(f"\n✓ Total EUR FX records: {len(df_euro)}")
    
    return df_euro

def process_cftc_positioning(df_raw):
    """
    Process CFTC data to extract Non-Commercial positioning
    
    Returns:
    - DataFrame with date, long, short, net, z-scores, percentile
    """
    df = df_raw.copy()
    
    # Parse date
    df['date'] = pd.to_datetime(df['Report_Date_as_YYYY-MM-DD'])
    
    # Extract Non-Commercial (speculative) positions
    df['long'] = pd.to_numeric(df['NonComm_Positions_Long_All'], errors='coerce')
    df['short'] = pd.to_numeric(df['NonComm_Positions_Short_All'], errors='coerce')
    
    # Calculate net position
    df['net_position'] = df['long'] - df['short']
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Keep only relevant columns
    df_clean = df[['date', 'long', 'short', 'net_position']].copy()
    
    # Remove any rows with missing data
    df_clean = df_clean.dropna()
    
    # Calculate rolling statistics
    # 6-month window (~26 weeks)
    df_clean['mean_6m'] = df_clean['net_position'].rolling(window=26, min_periods=20).mean()
    df_clean['std_6m'] = df_clean['net_position'].rolling(window=26, min_periods=20).std()
    df_clean['z_6m'] = (df_clean['net_position'] - df_clean['mean_6m']) / df_clean['std_6m']
    
    # 1-year window (~52 weeks)
    df_clean['mean_1y'] = df_clean['net_position'].rolling(window=52, min_periods=40).mean()
    df_clean['std_1y'] = df_clean['net_position'].rolling(window=52, min_periods=40).std()
    df_clean['z_1y'] = (df_clean['net_position'] - df_clean['mean_1y']) / df_clean['std_1y']
    
    # Historical percentile (full history)
    df_clean['percentile'] = df_clean['net_position'].rank(pct=True) * 100
    
    # Classification
    def classify_positioning(row):
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
    
    df_clean['positioning_state'] = df_clean.apply(classify_positioning, axis=1)
    
    return df_clean

def generate_positioning_commentary(state, z_6m, z_1y, percentile):
    """
    Generate institutional-style commentary based on positioning state
    
    Parameters:
    - state: Crowded Long, Crowded Short, or Neutral
    - z_6m, z_1y: Z-scores
    - percentile: Historical percentile
    
    Returns:
    - str: One-line commentary
    """
    if state == "Crowded Long":
        return "Positioning is crowded long, historically increasing downside asymmetry and sensitivity to negative macro or policy surprises."
    elif state == "Crowded Short":
        return "Positioning is crowded short, increasing squeeze risk if macro or policy dynamics turn supportive."
    else:
        return "Positioning is neutral, suggesting limited crowding-related asymmetry."

def save_positioning_data(output_dir='cftc_outputs'):
    """
    Fetch, process, and save CFTC positioning data
    """
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    print("="*80)
    print("FETCHING CFTC EUR POSITIONING DATA")
    print("="*80)
    
    # Fetch data
    df_raw = fetch_cftc_data()
    
    # Process
    print("\nProcessing positioning metrics...")
    df_processed = process_cftc_positioning(df_raw)
    
    # Get latest
    latest = df_processed.iloc[-1]
    
    # Generate commentary
    commentary = generate_positioning_commentary(
        latest['positioning_state'],
        latest['z_6m'],
        latest['z_1y'],
        latest['percentile']
    )
    
    # Create summary JSON
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
    csv_path = output_path / 'cftc_eur_positioning.csv'
    json_path = output_path / 'cftc_positioning_summary.json'
    
    df_processed.to_csv(csv_path, index=False)
    
    import json
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Saved: {csv_path}")
    print(f"✓ Saved: {json_path}")
    
    print("\n" + "="*80)
    print("LATEST POSITIONING")
    print("="*80)
    print(f"Date: {summary['date']}")
    print(f"Net Position: {summary['net_position']:,} contracts")
    print(f"  Long: {summary['long']:,}")
    print(f"  Short: {summary['short']:,}")
    print(f"Z-Score (6m): {summary['z_6m']:+.2f}σ")
    print(f"Z-Score (1y): {summary['z_1y']:+.2f}σ")
    print(f"Percentile: {summary['percentile']:.1f}%")
    print(f"State: {summary['positioning_state']}")
    print(f"\nCommentary: {summary['commentary']}")
    print("="*80)
    
    return df_processed, summary

if __name__ == '__main__':
    save_positioning_data()

