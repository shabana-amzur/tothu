@echo off
REM Stop all servers on Windows

echo Stopping all servers...

REM Stop backend (uvicorn)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Tothu Backend*" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Backend stopped
) else (
    echo Backend not running or already stopped
)

REM Stop frontend (node/npm)
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Tothu Frontend*" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Frontend stopped
) else (
    echo Frontend not running or already stopped
)

echo.
echo All servers stopped
pause
