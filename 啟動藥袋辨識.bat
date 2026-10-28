@echo off
cd /d "%~dp0"
start "藥袋辨識伺服器（請勿關閉）" cmd /k py server.py
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8081
