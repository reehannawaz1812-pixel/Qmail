@echo off
echo ===================================================
echo   QuMail - Quantum Secure Email Suite
echo ===================================================
echo.

:: Initialize Database and Models
echo [1/3] Preparing Quantum Database...
python quant-sec-server\server\manage.py makemigrations quantserver
python quant-sec-server\server\manage.py migrate

:: Start the Quantum Key Manager / Relay Server
echo [2/3] Starting Quantum Relay Server (Background)...
start "QuMail Server" cmd /k "python quant-sec-server\server\manage.py runserver 0.0.0.0:8000"

:: Wait for server
echo Waiting for server to initialize...
timeout /t 5 > nul

:: Launch Client
echo [3/3] Launching QuMail Interactive Interface...
cd quant-sec-client
python qumail_pyqt.py

echo.
echo QuMail Session Terminated.
pause