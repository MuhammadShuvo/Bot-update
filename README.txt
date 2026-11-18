OTP BOT - QUICK START

1. Install Python 3.10+ (Windows: tick "Add python.exe to PATH").
2. Edit start.bat (Windows) or start.sh (Linux): fill in your values.
   - BOT_TOKEN: from @BotFather
   - ADMINS: your Telegram user ID (@userinfobot)
   - SOURCE_GROUP_ID: group/channel where Teleroutex forwards SMS
   - OTP_GROUP_ID: a DIFFERENT group where the bot posts masked OTPs
   - CHANNEL_ID / CHANNEL_LINK: channel users must join
3. Add the bot to the source group and OTP group as admin
   (or disable privacy mode in @BotFather).
4. Double-click start.bat. First run installs libraries automatically.
5. In Telegram: /start -> ADMIN PANEL, then send your .txt/.csv number file
   to the bot in private chat (full numbers with country code, e.g. 8801892345612).
6. Test: GET NUMBER -> send a test SMS -> code appears, balance +0.80 BDT.

Alternative mode: set SMS_SOURCE=api and MESSAGES_URL=<endpoint> to poll
Teleroutex instead of reading a group.

SECURITY: never share your bot token or Teleroutex API key. Rotate any key
that has been pasted in public.

CONTROL PANEL (Windows, easiest)
Double-click start_controller.bat. Click "Install libraries" once, fill in settings,
click Save, then Start. You can stop/restart, view logs and stats, back up db.json.
Closing the panel stops the bot. Keep the window open (minimized) while the bot runs.

DOCKER DESKTOP
1. Install Docker Desktop (needs WSL2, the installer sets it up).
2. Edit .env with your values (no quotes).
3. In this folder run:  docker compose up -d --build
4. Logs: docker compose logs -f     Stop: docker compose down
Your data (db.json) is saved in the ./data folder - back it up.
