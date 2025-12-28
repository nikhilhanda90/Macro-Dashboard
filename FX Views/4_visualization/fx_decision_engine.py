"""
FX Decision Engine
Rules-based synthesis of Layer 1 (Valuation) + Layer 2 (Pressure) + Technicals + Positioning
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Determine base directory (FX Views root)
SCRIPT_DIR = Path(__file__).parent
FX_VIEWS_ROOT = SCRIPT_DIR.parent

def get_valuation_signal(z_score):
    """
    Classify valuation regime
    Returns: ('Cheap' | 'Fair' | 'Rich', status_text)
    """
    if z_score <= -2:
        return 'Cheap', f'{z_score:.2f}σ (Break)'
    elif z_score <= -1:
        return 'Cheap', f'{z_score:.2f}σ (Stretch)'
    elif z_score >= 2:
        return 'Rich', f'{z_score:.2f}σ (Break)'
    elif z_score >= 1:
        return 'Rich', f'{z_score:.2f}σ (Stretch)'
    else:
        return 'Fair', f'{z_score:.2f}σ'

def get_pressure_signal(pressure_label, prob_expand, confidence):
    """
    Format pressure signal
    Returns: ('Expanding' | 'Compressing', status_text)
    """
    direction = 'Expanding' if pressure_label == 'expand' else 'Compressing'
    status = f"{direction} ({int(prob_expand*100)}% conf, {confidence.capitalize()})"
    return direction, status

def get_technical_signal(technical_data):
    """
    Extract technical bias
    Returns: ('Bullish' | 'Neutral' | 'Bearish', status_text)
    """
    regime = technical_data.get('regime', 'Neutral')
    score = technical_data.get('technical_score', 0)
    
    if regime in ['Bullish', 'Strongly Bullish']:
        bias = 'Bullish'
    elif regime in ['Bearish', 'Strongly Bearish']:
        bias = 'Bearish'
    else:
        bias = 'Neutral'
    
    status = f"{regime} (Score: {score:.1f})"
    return bias, status

def get_positioning_signal(positioning_data):
    """
    Extract positioning bias
    Returns: ('Crowded Long' | 'Crowded Short' | 'Neutral' | 'Clean', status_text)
    """
    state = positioning_data.get('positioning_state', 'Neutral')
    percentile = positioning_data.get('percentile', 50)
    
    if state == 'Crowded Long':
        bias = 'Crowded Long'
    elif state == 'Crowded Short':
        bias = 'Crowded Short'
    elif state == 'Neutral':
        bias = 'Neutral'
    else:
        bias = 'Clean'
    
    status = f"{state} ({percentile:.0f}th percentile)"
    return bias, status

def determine_implication(val_regime, pressure_dir, tech_bias, pos_bias):
    """
    One-line synthesis for action bias
    Priority: Valuation × Pressure > Technicals > Positioning
    """
    # Primary logic: Valuation × Pressure
    if val_regime == 'Rich' and pressure_dir == 'Expanding':
        primary = "Momentum dominates → don't fade"
    elif val_regime == 'Rich' and pressure_dir == 'Compressing':
        primary = "Overvaluation fading → fade rallies"
    elif val_regime == 'Cheap' and pressure_dir == 'Expanding':
        primary = "Upside pressure → buy dips / trend continuation"
    elif val_regime == 'Cheap' and pressure_dir == 'Compressing':
        primary = "Rebound fragile → wait for confirmation / be selective"
    elif val_regime == 'Fair' and pressure_dir == 'Expanding':
        primary = "Momentum building from fair value"
    elif val_regime == 'Fair' and pressure_dir == 'Compressing':
        primary = "Consolidation around fair value"
    else:
        primary = "Mixed signals"
    
    # Technical modifier
    if tech_bias == 'Bullish':
        tech_add = ", but trend is supportive"
    elif tech_bias == 'Bearish':
        tech_add = ", but trend is heavy"
    else:
        tech_add = ""
    
    # Positioning modifier
    if pos_bias in ['Crowded Long', 'Crowded Short']:
        pos_add = ", crowding raises reversal risk"
    elif pos_bias == 'Clean':
        pos_add = ", asymmetry less crowded"
    else:
        pos_add = ""
    
    # Combine (keep to one line)
    return primary + tech_add + pos_add

def generate_nikhil_view(val_regime, val_z, pressure_dir, prob_expand, confidence, 
                         tech_bias, pos_bias, spot, fair_value):
    """
    FX Views Language Rules (Critical):
    - CFO View: ACTION + CONDITIONS (2 lines, no jargon)
    - Analyst View: Bullets + "So what"
    """
    pair = "EURUSD"
    
    # Normalize inputs
    val_state = val_regime.lower()  # rich, cheap, fair
    pressure_state = pressure_dir.lower()  # expanding, compressing
    tech_state = tech_bias.lower()  # bullish, neutral, bearish
    pos_state = pos_bias.lower()  # crowded long, crowded short, neutral, clean
    
    # Confidence threshold
    pressure_prob_actual = prob_expand if pressure_state == 'expanding' else (1 - prob_expand)
    confidence_pct = int(pressure_prob_actual * 100)
    
    # ========== CFO VIEW — "WHAT DO I DO?" (2 LINES MAX) ==========
    # Structure: ACTION (bold) + CONDITIONS
    # NO jargon, NO model names, NO σ
    
    # Mapping table: Valuation × Pressure → Action + Conditions
    if val_state == 'rich' and pressure_state == 'compressing':
        action = f"Fade {pair} rallies. Don't chase upside."
        if tech_state == 'bearish':
            conditions = "View breaks if pressure re-accelerates."
        else:
            conditions = "Not a conviction short. View breaks if upside pressure re-accelerates."
    
    elif val_state == 'rich' and pressure_state == 'expanding':
        action = f"Stay neutral on {pair}. Don't fade on valuation alone."
        conditions = "View breaks if technicals roll or positioning crowds."
    
    elif val_state == 'cheap' and pressure_state == 'expanding':
        action = f"Buy {pair} dips. Don't fade strength."
        if tech_state == 'bullish':
            conditions = "View breaks if pressure flips to compressing."
        else:
            conditions = "Not full conviction yet. View breaks if pressure flips to compressing."
    
    elif val_state == 'cheap' and pressure_state == 'compressing':
        action = f"Wait on {pair}. Value alone is insufficient."
        conditions = "View breaks if pressure re-expands or technicals turn bullish."
    
    elif val_state == 'fair' and pressure_state == 'expanding':
        action = f"Trade {pair} momentum tactically. Don't marry the position."
        conditions = "View breaks if momentum stalls or valuation moves to an extreme."
    
    else:  # fair + compressing
        action = f"Stay neutral on {pair}. Wait for clearer regime."
        conditions = "View breaks if valuation moves beyond neutral or pressure reverses."
    
    # CFO View = ACTION + CONDITIONS (structured for UI parsing)
    cfo_view = f"ACTION|||{action}\nCONDITIONS|||{conditions}"
    cfo_headline = action  # For backward compatibility
    
    # ========== ANALYST VIEW — BULLETS + "SO WHAT" ==========
    # Structure: One line each for Valuation, Pressure, Technicals, Positioning + So what section
    # Limited jargon; no repetition
    
    # Valuation bullet (ElasticNet, plain English)
    if abs(val_z) >= 2:
        val_desc = f"Valuation: Stretched {val_state} ({val_z:+.1f}σ vs macro fair value); snapback risk is elevated."
    elif abs(val_z) >= 1:
        val_desc = f"Valuation: Moderately {val_state} ({val_z:+.1f}σ vs macro fair value)."
    else:
        val_desc = f"Valuation: Near fair value ({val_z:+.1f}σ)."
    
    # Pressure bullet (LightGBM, plain English)
    pressure_desc = f"Pressure: Weekly signals show {pressure_state} ({confidence_pct}% probability); forces {'pushing the gap wider' if pressure_state == 'expanding' else 'working to close the gap'}."
    
    # Technicals bullet (one line)
    if tech_state == 'bullish':
        tech_desc = "Technicals: Trend is constructive; no signs of reversal yet."
    elif tech_state == 'bearish':
        tech_desc = "Technicals: Momentum has turned negative; downside follow-through is likely."
    else:
        tech_desc = "Technicals: Neutral; provides little directional signal."
    
    # Positioning bullet (one line)
    if 'crowded' in pos_state:
        if 'long' in pos_state:
            pos_desc = "Positioning: Crowded long; unwind risk if sentiment shifts."
        else:
            pos_desc = "Positioning: Crowded short; squeeze risk if catalysts turn positive."
    elif pos_state == 'neutral':
        pos_desc = "Positioning: Neutral; no material asymmetry."
    else:
        pos_desc = "Positioning: Clean; tail risk is limited."
    
    # "So what" section - synthesis
    if val_state == 'rich' and pressure_state == 'compressing':
        so_what = "The setup supports fading rallies, but technicals and positioning haven't confirmed yet—so keep it tactical, not conviction."
    elif val_state == 'rich' and pressure_state == 'expanding':
        so_what = "Valuation is stretched, but momentum still dominates—wait for a technical crack before positioning short."
    elif val_state == 'cheap' and pressure_state == 'expanding':
        so_what = "Both valuation and pressure favor upside—dips are buyable unless pressure reverses."
    elif val_state == 'cheap' and pressure_state == 'compressing':
        so_what = "Valuation is supportive, but market behavior isn't confirming yet—wait for pressure to re-expand."
    elif val_state == 'fair' and pressure_state == 'expanding':
        so_what = "This is a momentum play, not a value play—trade it tactically, don't hold through reversals."
    else:  # fair + compressing
        so_what = "No strong directional signal from fundamentals or flows—reduce conviction and wait."
    
    # Combine into Analyst View (bullets + So what)
    analyst_view = f"""• {val_desc}
• {pressure_desc}
• {tech_desc}
• {pos_desc}

So what:
{so_what}"""
    
    return cfo_headline, cfo_view, analyst_view

def build_decision_summary():
    """
    Load latest data from all 4 layers and generate decision summary
    Returns: dict with all signals and synthesis
    """
    print("\n[FX DECISION ENGINE]")
    
    # Layer 1: Valuation (monthly)
    layer1_path = FX_VIEWS_ROOT / '2_layer1_models' / 'fx_layer1_outputs' / 'elasticnet_predictions.csv'
    layer1_df = pd.read_csv(layer1_path, parse_dates=['date'])
    latest_val = layer1_df.iloc[-1]
    
    val_date = latest_val['date']
    val_spot = latest_val['spot']
    val_fv = latest_val['fair_value']
    val_z = latest_val['mispricing_z']
    val_regime = latest_val['regime']
    
    val_signal, val_status = get_valuation_signal(val_z)
    print(f"  Layer 1 (Valuation): {val_signal} — {val_status}")
    
    # Layer 2: Pressure (weekly)
    layer2_path = FX_VIEWS_ROOT / '3_layer2_models' / 'fx_layer2_outputs' / 'lightgbm_binary_predictions.csv'
    layer2_df = pd.read_csv(layer2_path, parse_dates=['date'])
    latest_pressure = layer2_df.iloc[-1]
    
    pressure_date = latest_pressure['date']
    pressure_label = latest_pressure['pressure_label']
    prob_expand = latest_pressure['prob_expand']
    confidence = latest_pressure['confidence']
    
    pressure_signal, pressure_status = get_pressure_signal(pressure_label, prob_expand, confidence)
    print(f"  Layer 2 (Pressure): {pressure_signal} — {pressure_status}")
    
    # Layer 3: Technicals
    tech_path = FX_VIEWS_ROOT / 'technical_outputs' / 'eurusd_technical_summary.json'
    if tech_path.exists():
        tech_data = json.load(open(tech_path, 'r'))
        tech_signal, tech_status = get_technical_signal(tech_data)
        print(f"  Layer 3 (Technicals): {tech_signal} — {tech_status}")
    else:
        tech_signal, tech_status = 'Neutral', 'No data'
        print(f"  Layer 3 (Technicals): {tech_signal} — {tech_status}")
    
    # Layer 4: Positioning
    pos_path = FX_VIEWS_ROOT / 'cftc_outputs' / 'cftc_positioning_summary.json'
    if pos_path.exists():
        pos_data = json.load(open(pos_path, 'r'))
        pos_signal, pos_status = get_positioning_signal(pos_data)
        print(f"  Layer 4 (Positioning): {pos_signal} — {pos_status}")
    else:
        pos_signal, pos_status = 'Neutral', 'No data'
        print(f"  Layer 4 (Positioning): {pos_signal} — {pos_status}")
    
    # Determine implication
    implication = determine_implication(val_signal, pressure_signal, tech_signal, pos_signal)
    print(f"\n  Implication: {implication}")
    
    # Generate Nikhil FX View (CFO + Analyst split)
    cfo_headline, cfo_view, analyst_view = generate_nikhil_view(
        val_signal, val_z, pressure_signal, prob_expand, confidence,
        tech_signal, pos_signal, val_spot, val_fv
    )
    print(f"\n  CFO Headline: {cfo_headline}")
    print(f"  CFO View: {cfo_view}")
    print(f"  Analyst View: {analyst_view}")
    
    # Package results
    decision = {
        'pair': 'EURUSD',
        'cfo_headline': cfo_headline,
        'cfo_view': cfo_view,
        'analyst_view': analyst_view,
        'nikhil_view': cfo_view,  # For backward compatibility
        'regime_label': cfo_headline,  # For backward compatibility
        'layers': {
            'valuation': {
                'signal': val_signal,
                'status': val_status,
                'spot': val_spot,
                'fair_value': val_fv,
                'z_score': val_z,
                'date': val_date.strftime('%Y-%m-%d')
            },
            'pressure': {
                'signal': pressure_signal,
                'status': pressure_status,
                'label': pressure_label,
                'prob_expand': prob_expand,
                'confidence': confidence,
                'date': pressure_date.strftime('%Y-%m-%d')
            },
            'technical': {
                'signal': tech_signal,
                'status': tech_status
            },
            'positioning': {
                'signal': pos_signal,
                'status': pos_status
            }
        },
        'implication': implication,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to JSON
    output_path = FX_VIEWS_ROOT / '5_outputs' / 'eurusd_fx_views_decision.json'
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(decision, f, indent=2)
    
    print(f"\n[OK] Decision summary saved: {output_path}")
    
    return decision

if __name__ == "__main__":
    decision = build_decision_summary()
    print("\n" + "="*80)
    print("[SUCCESS] FX Decision Engine complete")
    print("="*80)
