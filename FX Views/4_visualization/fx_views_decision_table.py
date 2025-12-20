"""
FX Views Decision Table
Converts Layer 1 (valuation) × Layer 2 (pressure) → Actionable stance
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path

def get_valuation_bucket(z_val):
    """Convert z-score to valuation bucket"""
    if z_val <= -2.0:
        return "CHEAP_BREAK", "cheap"
    elif z_val <= -1.0:
        return "CHEAP_STRETCH", "cheap"
    elif z_val < 1.0:
        return "FAIR", "fair"
    elif z_val < 2.0:
        return "RICH_STRETCH", "rich"
    else:
        return "RICH_BREAK", "rich"

def get_pressure_direction(delta_z_pred):
    """Convert predicted Δz to pressure direction"""
    if delta_z_pred < 0:
        return "compress"
    else:
        return "expand"

def get_pressure_confidence(delta_z_pred, threshold_high=0.3, threshold_med=0.15):
    """Estimate confidence from magnitude of prediction"""
    abs_pred = abs(delta_z_pred)
    if abs_pred >= threshold_high:
        return "high"
    elif abs_pred >= threshold_med:
        return "med"
    else:
        return "low"

# Decision Matrix: 5 valuation buckets × 2 pressure directions = 10 stances
DECISION_MATRIX = {
    ("CHEAP_BREAK", "compress"): {
        "stance_title": "Mean Reversion Setup",
        "stance_badge": "Rebound",
        "stance_summary": "EUR looks extremely cheap vs macro, and pressure suggests mean reversion has started.",
        "watchouts": "Momentum overrides can delay the turn—watch vol spikes.",
        "action_bias": "Mean-revert"
    },
    ("CHEAP_BREAK", "expand"): {
        "stance_title": "Knife Catch Risk",
        "stance_badge": "Caution",
        "stance_summary": "EUR looks extremely cheap, but pressure still points to further cheapening.",
        "watchouts": "Wait for pressure to flip before sizing conviction.",
        "action_bias": "Caution"
    },
    ("CHEAP_STRETCH", "compress"): {
        "stance_title": "Attractive Mean Reversion",
        "stance_badge": "Buy-the-dip",
        "stance_summary": "EUR is cheap vs macro, and pressure supports normalization.",
        "watchouts": "If risk-off spikes, cheap can get cheaper.",
        "action_bias": "Mean-revert"
    },
    ("CHEAP_STRETCH", "expand"): {
        "stance_title": "Early, Not Yet",
        "stance_badge": "Wait",
        "stance_summary": "EUR is cheap, but pressure indicates the market is still leaning away from value.",
        "watchouts": "Look for technical stabilization before conviction.",
        "action_bias": "Caution"
    },
    ("FAIR", "compress"): {
        "stance_title": "Range / Normalization",
        "stance_badge": "Neutral",
        "stance_summary": "EUR is near fair value, and pressure suggests mean reversion / range behavior.",
        "watchouts": "Catalysts matter more than valuation here.",
        "action_bias": "Neutral"
    },
    ("FAIR", "expand"): {
        "stance_title": "Trend Building",
        "stance_badge": "Watch",
        "stance_summary": "EUR is near fair value, but pressure suggests a new trend may be forming.",
        "watchouts": "Confirm with technicals and risk regime.",
        "action_bias": "Trend"
    },
    ("RICH_STRETCH", "compress"): {
        "stance_title": "Overvaluation Fading",
        "stance_badge": "Fade",
        "stance_summary": "EUR looks rich vs macro, and pressure suggests mispricing is compressing.",
        "watchouts": "Momentum bursts can extend rallies temporarily.",
        "action_bias": "Mean-revert"
    },
    ("RICH_STRETCH", "expand"): {
        "stance_title": "Momentum vs Value",
        "stance_badge": "Trend",
        "stance_summary": "EUR is rich, and pressure still supports further richening—trend may dominate near-term.",
        "watchouts": "Risk of sharp snapback rises as z approaches +2σ.",
        "action_bias": "Trend"
    },
    ("RICH_BREAK", "compress"): {
        "stance_title": "Mean Reversion Risk High",
        "stance_badge": "Reversal",
        "stance_summary": "EUR is extremely rich vs macro, and pressure suggests reversion is underway.",
        "watchouts": "Crowded positioning can still whip around—use confirmation.",
        "action_bias": "Mean-revert"
    },
    ("RICH_BREAK", "expand"): {
        "stance_title": "Blow-off / Late Trend",
        "stance_badge": "Danger",
        "stance_summary": "EUR is extremely rich and still getting richer—late-cycle trend behavior.",
        "watchouts": "Highest snapback risk—treat as fragile.",
        "action_bias": "Caution"
    }
}

def generate_decision(z_val, delta_z_pred):
    """
    Generate decision stance from valuation + pressure
    
    Args:
        z_val: Current mispricing z-score (from Layer 1)
        delta_z_pred: Predicted change in z (from Layer 2)
    
    Returns:
        dict with decision stance
    """
    val_bucket, val_sign = get_valuation_bucket(z_val)
    pressure_dir = get_pressure_direction(delta_z_pred)
    pressure_conf = get_pressure_confidence(delta_z_pred)
    
    # Look up stance from matrix
    stance = DECISION_MATRIX.get((val_bucket, pressure_dir), {
        "stance_title": "Unknown Configuration",
        "stance_badge": "Review",
        "stance_summary": "Unusual valuation/pressure combination—review manually.",
        "watchouts": "Check data quality.",
        "action_bias": "Neutral"
    })
    
    # Build full decision object
    decision = {
        "inputs": {
            "z_val": float(z_val),
            "val_bucket": val_bucket,
            "val_sign": val_sign,
            "delta_z_pred": float(delta_z_pred),
            "pressure_dir": pressure_dir,
            "pressure_conf": pressure_conf
        },
        "stance": stance
    }
    
    return decision

if __name__ == "__main__":
    print("="*80)
    print("FX VIEWS DECISION TABLE")
    print("="*80)
    
    # Load latest Layer 1 valuation
    print("\n[1] Loading Layer 1 (monthly valuation)...")
    layer1_rec = json.load(open('fx_layer1_outputs/layer1_recommendation.json', 'r'))
    layer1_models = pd.read_pickle('fx_layer1_outputs/all_models.pkl')
    
    model_key = layer1_rec['selected_model']
    sigma = layer1_rec['metrics']['sigma']
    monthly_full = layer1_models[model_key]['monthly_full']
    
    # Get latest month
    latest_month = monthly_full.iloc[-1]
    z_val = latest_month['z_score']
    spot = latest_month['spot']
    fv = latest_month['fair_value']
    regime = latest_month['regime']
    
    print(f"  Latest month: {latest_month['date'].strftime('%Y-%m')}")
    print(f"  Spot: {spot:.4f}")
    print(f"  Fair Value: {fv:.4f}")
    print(f"  Z-score: {z_val:+.2f}σ")
    print(f"  Regime: {regime}")
    
    # Load latest Layer 2 pressure
    print("\n[2] Loading Layer 2 (weekly pressure)...")
    layer2_models = pd.read_pickle('fx_layer2_outputs/all_models.pkl')
    layer2_rec = json.load(open('fx_layer2_outputs/layer2_recommendation.json', 'r'))
    
    target = layer2_rec['target']
    model_key2 = layer2_rec['model_key']
    
    # Get test predictions (latest available)
    test_pred = layer2_models[target][model_key2]['test_pred']
    delta_z_pred = test_pred[-1]  # Most recent prediction
    
    test_dates = layer2_models['test_dates']
    latest_week = test_dates[-1]
    
    print(f"  Latest week: {latest_week.strftime('%Y-%m-%d')}")
    print(f"  Predicted Δz: {delta_z_pred:+.3f}")
    print(f"  Direction: {'Compressing' if delta_z_pred < 0 else 'Expanding'}")
    
    # Generate decision
    print("\n[3] Generating decision stance...")
    decision = generate_decision(z_val, delta_z_pred)
    
    # Display
    print("\n" + "="*80)
    print("DECISION OUTPUT")
    print("="*80)
    
    print(f"\nINPUTS:")
    print(f"  Valuation: {decision['inputs']['z_val']:+.2f}σ ({decision['inputs']['val_bucket']})")
    print(f"  Pressure: {decision['inputs']['pressure_dir'].upper()} ({decision['inputs']['pressure_conf']} confidence)")
    
    print(f"\nSTANCE:")
    print(f"  Title: {decision['stance']['stance_title']}")
    print(f"  Badge: {decision['stance']['stance_badge']}")
    print(f"  Bias: {decision['stance']['action_bias']}")
    
    print(f"\n  Summary:")
    print(f"  {decision['stance']['stance_summary']}")
    
    print(f"\n  Watchouts:")
    print(f"  {decision['stance']['watchouts']}")
    
    # Save to JSON
    output_path = 'fx_views_outputs/eurusd_fx_views_decision.json'
    Path('fx_views_outputs').mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(decision, f, indent=2)
    
    print(f"\n[OK] Saved: {output_path}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Decision table generated!")
    print("="*80)

