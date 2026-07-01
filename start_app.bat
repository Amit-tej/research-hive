@echo off
echo Starting Research Hive Application...

REM Create middleware directory if it doesn't exist
if not exist "c:\Users\bharg\Downloads\Research Hive\middleware" mkdir "c:\Users\bharg\Downloads\Research Hive\middleware"

REM Create cache directory if it doesn't exist
if not exist "c:\Users\bharg\Downloads\Research Hive\cache" mkdir "c:\Users\bharg\Downloads\Research Hive\cache"

REM Start the API server in a new window
start cmd /k "cd c:\Users\bharg\Downloads\Research Hive\middleware && python api_server.py"

REM Wait for the API server to start
timeout /t 3 /nobreak

REM Start your existing application from the hary directory
cd c:\Users\bharg\Downloads\Research Hive\hary
python app.py