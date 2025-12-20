"""
Generate Complete Technical Analysis
Runs both indicator calculation and chart generation
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the two modules
import eurusd_technicals
import eurusd_technical_charts

def main():
    print("\n" + "="*80)
    print("COMPLETE TECHNICAL ANALYSIS GENERATION")
    print("="*80)
    print("\n[1/2] Calculating indicators...")
    
    # Step 1: Calculate indicators
    try:
        df, summary = eurusd_technicals.run_technical_analysis()
        print("✓ Indicators complete")
    except Exception as e:
        print(f"❌ Indicator calculation failed: {e}")
        return
    
    print("\n[2/2] Generating charts...")
    
    # Step 2: Generate charts
    try:
        eurusd_technical_charts.generate_charts()
        print("✓ Charts complete")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return
    
    print("\n" + "="*80)
    print("✅ ALL TECHNICAL ANALYSIS COMPLETE")
    print("="*80)
    print("\nOutputs:")
    print("  • technical_outputs/eurusd_technical_data.csv")
    print("  • technical_outputs/eurusd_technical_summary.json")
    print("  • technical_outputs/eurusd_technical_chart.html")
    print("\n📊 Refresh your dashboard to see the candlestick chart!")

if __name__ == '__main__':
    main()

