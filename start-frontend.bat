@echo off
title VCT Match Predictor - App
cd /d "%~dp0client"
echo Starting app on http://localhost:5173
echo.
npm run dev
pause
