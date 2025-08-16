@echo off
echo =====================================================
echo     HHA Medicine - Medical Billing KPI Dashboard
echo =====================================================
echo.
echo Starting the dashboard application...
echo.

cd /d "%~dp0\..\02_Backend_Server"
echo Installing required packages...
pip install -r requirements.txt > nul 2>&1

echo.
echo Starting server...
echo Dashboard will open at: http://localhost:5010
echo.
start http://localhost:5010
python main_server.py

pause