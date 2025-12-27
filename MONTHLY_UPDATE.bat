@echo off
echo ========================================
echo MONTHLY FX VIEWS UPDATE (Layer 1)
echo ========================================
echo.
echo This will:
echo   1. Retrain Layer 1 ElasticNet with latest macro data
echo   2. Generate fresh fair value predictions
echo   3. Run weekly update (Layer 2, charts, technicals, positioning)
echo.
echo Run this ONCE A MONTH when new macro data is available
echo (e.g. when latest US/Eurozone data published)
echo.
pause
echo.

REM Step 1: Retrain Layer 1 (ElasticNet)
echo [STEP 1] Retraining Layer 1 (ElasticNet) with latest macro data...
cd /d "C:\Users\NikhilHanda\FX Views\2_layer1_models"
py fx_layer1_monthly_valuation.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Layer 1 training failed!
    echo Check that latest macro data is available.
    pause
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Layer 1 retrained successfully!
echo.
pause
echo.

REM Step 2: Run weekly update (which includes Layer 2)
echo [STEP 2] Running weekly update (Layer 2, charts, technicals, positioning)...
cd /d "C:\Users\NikhilHanda\Documents\Macro-Dashboard"
call WEEKLY_UPDATE.bat

echo.
echo ========================================
echo MONTHLY UPDATE COMPLETE!
echo ========================================
echo.
echo Layer 1 (Valuation): UPDATED with latest macro data
echo Layer 2 (Pressure): UPDATED with latest weekly data
echo Charts: REGENERATED
echo Technicals: REFRESHED
echo Positioning: REFRESHED
echo.
pause

