@echo off
echo ========================================
echo WEEKLY FX VIEWS UPDATE
echo ========================================
echo.
echo This will:
echo   1. Generate fresh FX Views charts
echo   2. Update technical analysis
echo   3. Fetch latest CFTC positioning
echo   4. Create decision summary
echo.
echo Run this EVERY TUESDAY after market close
echo Then commit and push to GitHub
echo.
pause
echo.

REM Step 1: Retrain Layer 2 (LightGBM Binary) with latest weekly data
echo [STEP 1] Retraining Layer 2 (Pressure Model) with latest weekly data...
cd /d "C:\Users\NikhilHanda\FX Views\3_layer2_models"
py fx_layer2_lightgbm_only.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Layer 2 training failed. Using old predictions.
    echo.
)

echo.
REM Step 2: Generate FX Views charts and decision
echo [STEP 2] Generating FX Views charts and decision...
cd /d "C:\Users\NikhilHanda\FX Views"
py generate_fx_views_complete.py

echo.
echo [STEP 3] Copying to Dashboard folder...
xcopy "C:\Users\NikhilHanda\FX Views\3_layer2_models\fx_layer2_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\3_layer2_models\fx_layer2_outputs\" /Y /I
xcopy "C:\Users\NikhilHanda\FX Views\5_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\5_outputs\" /Y
xcopy "C:\Users\NikhilHanda\FX Views\technical_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\technical_outputs\" /Y
xcopy "C:\Users\NikhilHanda\FX Views\cftc_outputs\*" "C:\Users\NikhilHanda\Documents\Macro-Dashboard\FX Views\cftc_outputs\" /Y

echo.
echo ========================================
echo UPDATE COMPLETE!
echo ========================================
echo.
echo What was updated:
echo   - Layer 2 (Pressure): Retrained with latest weekly data
echo   - Charts: Regenerated with fresh predictions
echo   - Technicals: Refreshed from Yahoo Finance
echo   - Positioning: Refreshed from CFTC
echo.
echo Next steps:
echo   1. cd "C:\Users\NikhilHanda\Documents\Macro-Dashboard"
echo   2. git add FX Views/3_layer2_models/fx_layer2_outputs/*
echo   3. git add FX Views/5_outputs/*
echo   4. git add FX Views/technical_outputs/*
echo   5. git add FX Views/cftc_outputs/*
echo   6. git commit -m "Weekly FX Views update - [TODAY]"
echo   7. git push origin main
echo.
echo Streamlit Cloud will auto-deploy in 1-2 minutes!
echo.
pause

