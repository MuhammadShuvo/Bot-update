@echo off
cd /d %~dp0
python controller.py
if errorlevel 1 pause
