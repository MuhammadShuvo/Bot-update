#!/bin/bash
cd "$(dirname "$0")"
[ -d venv ] || { python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt; }
source venv/bin/activate
export BOT_TOKEN="PUT_BOT_TOKEN_HERE"
export ADMINS="1647484306"
export SOURCE_GROUP_ID="-100PUT_SOURCE_GROUP_ID"
export OTP_GROUP_ID="-100PUT_PUBLIC_OTP_GROUP_ID"
export CHANNEL_ID="-100PUT_FORCE_JOIN_CHANNEL_ID"
export CHANNEL_LINK="https://t.me/yourchannel"
python bot.py
