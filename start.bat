@echo off
cd /d %~dp0
python -c "import telegram, httpx, pyotp" 2>nul || python -m pip install -r requirements.txt
REM ---- EDIT THESE VALUES (no quotes) ----
set BOT_TOKEN=PUT_BOT_TOKEN_HERE
set ADMINS=1647484306
REM Public OTP group: leave as is and send /setotpgroup inside the group in Telegram (bot must be admin there)
set OTP_GROUP_ID=0
set CHANNEL_ID=-100PUT_FORCE_JOIN_CHANNEL_ID
set CHANNEL_LINK=https://t.me/yourchannel
set SUPPORT_LINK=https://t.me/yoursupport
set DEVELOPER_LINK=https://t.me/yoursupport
REM ---- SMS source: api = read codes from Teleroutex API ----
set SMS_SOURCE=api
set TELEROUTEX_API_KEY=PUT_NEW_TELEROUTEX_API_KEY_HERE
REM SOURCE_GROUP_ID is not used in api mode (leave 0). For group mode set SMS_SOURCE=group and your group ID.
set SOURCE_GROUP_ID=0
REM ---- numbers per tap / minutes each number is valid ----
set NUMBERS_PER_REQUEST=3
set OTP_VALID_MINUTES=10
REM ---- after Change Number, old numbers keep delivering OTPs: 0 = no time limit, or a number of minutes ----
set KEEP_OLD_MINUTES=0
REM ---- 1 = pay for every OTP on a number, 0 = only the first ----
set PAY_EVERY_OTP=1
REM ---- digits of the code visible in the public OTP group (0 = fully hidden) ----
set OTP_PUBLIC_VISIBLE_DIGITS=0
REM ---- hours added to UTC for the time shown in the public group (6 = Bangladesh) ----
set TIMEZONE_HOURS=6
REM ---------------------------------------
python bot.py
pause
