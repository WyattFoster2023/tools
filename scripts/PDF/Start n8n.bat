@echo off
echo Starting ngrok tunnel on port 5678...
start "" ngrok http 5678

timeout /t 3 >nul

echo Starting n8n...
n8n start
