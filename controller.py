"""Windows control panel for the OTP bot: start/stop, settings, logs, stats, backup."""
import json, os, queue, re, shutil, subprocess, sys, threading, time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(BASE, "config.json")
DB = os.path.join(BASE, "db.json")
FIELDS = [("BOT_TOKEN", "Bot token"), ("ADMINS", "Admin user ID(s), comma separated"),
          ("SOURCE_GROUP_ID", "Source group ID (Teleroutex forwards here)"),
          ("OTP_GROUP_ID", "Public OTP group ID (different group)"),
          ("CHANNEL_ID", "Force-join channel ID"), ("CHANNEL_LINK", "Force-join channel link"),
          ("SMS_SOURCE", "SMS source: group or api"), ("TELEROUTEX_API_KEY", "Teleroutex API key (api mode)")]

def load_cfg():
    try:
        return json.load(open(CFG, encoding="utf-8"))
    except Exception:
        return {}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OTP Bot Control Panel")
        self.geometry("760x640")
        self.proc, self.q = None, queue.Queue()
        cfg = load_cfg()

        f = ttk.LabelFrame(self, text="Settings"); f.pack(fill="x", padx=10, pady=8)
        self.vars = {}
        for i, (k, label) in enumerate(FIELDS):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", padx=6, pady=2)
            v = tk.StringVar(value=cfg.get(k, ""))
            ttk.Entry(f, textvariable=v, width=55, show="*" if k in ("BOT_TOKEN", "TELEROUTEX_API_KEY") else "").grid(row=i, column=1, padx=6)
            self.vars[k] = v
        ttk.Button(f, text="Save settings", command=self.save).grid(row=len(FIELDS), column=1, sticky="e", pady=4)

        b = ttk.Frame(self); b.pack(fill="x", padx=10)
        self.status = ttk.Label(b, text="● STOPPED", foreground="red", font=("Segoe UI", 11, "bold"))
        self.status.pack(side="left", padx=4)
        for text, cmd in [("Start", self.start_bot), ("Stop", self.stop_bot), ("Restart", self.restart),
                          ("Stats", self.stats), ("Backup DB", self.backup),
                          ("Add numbers (bot stopped)", self.add_numbers), ("Install libraries", self.install)]:
            ttk.Button(b, text=text, command=cmd).pack(side="left", padx=3)

        self.log = tk.Text(self, height=22, bg="#111", fg="#0f0", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=8)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(300, self.pump)

    def write(self, s):
        self.log.insert("end", s + "\n"); self.log.see("end")

    def save(self):
        json.dump({k: v.get().strip() for k, v in self.vars.items()}, open(CFG, "w", encoding="utf-8"), indent=2)
        self.write("Settings saved.")

    def running(self):
        return self.proc is not None and self.proc.poll() is None

    def start_bot(self):
        if self.running():
            return self.write("Already running.")
        self.save()
        cfg = load_cfg()
        if not cfg.get("BOT_TOKEN"):
            return messagebox.showerror("Missing", "Enter the bot token first.")
        env = {**os.environ, **{k: v for k, v in cfg.items() if v}, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.proc = subprocess.Popen([sys.executable, "bot.py"], cwd=BASE, env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                                     creationflags=flags)
        threading.Thread(target=self.reader, daemon=True).start()
        self.write("Starting bot...")

    def reader(self):
        for line in self.proc.stdout:
            self.q.put(line.rstrip())
        self.q.put("[bot process ended]")

    def stop_bot(self):
        if self.running():
            self.proc.terminate()
            try:
                self.proc.wait(5)
            except Exception:
                self.proc.kill()
            self.write("Bot stopped.")

    def restart(self):
        self.stop_bot(); time.sleep(1); self.start_bot()

    def pump(self):
        while not self.q.empty():
            self.write(self.q.get())
        r = self.running()
        self.status.config(text="● RUNNING" if r else "● STOPPED", foreground="green" if r else "red")
        self.after(300, self.pump)

    def stats(self):
        try:
            d = json.load(open(DB, encoding="utf-8"))
        except Exception:
            return self.write("No db.json yet.")
        u = d["users"].values()
        pend = [w for w in d["withdraws"].values() if w["status"] == "pending"]
        self.write(f"Users: {len(d['users'])} | Numbers in pools: {sum(len(v) for v in d.get('pools', {}).values()) + len(d['pool'])} | "
                   f"OTPs: {sum(x['otps'] for x in u)} | Balances: {sum(x['balance'] for x in u):.2f} BDT | "
                   f"Pending withdrawals: {len(pend)}")

    def backup(self):
        if not os.path.exists(DB):
            return self.write("No db.json to back up.")
        os.makedirs(os.path.join(BASE, "backups"), exist_ok=True)
        dst = os.path.join(BASE, "backups", time.strftime("db_%Y%m%d_%H%M%S.json"))
        shutil.copy(DB, dst); self.write(f"Backup saved: {dst}")

    def add_numbers(self):
        if self.running():
            return messagebox.showwarning("Stop the bot first", "Stop the bot before editing numbers here, "
                                          "or send the file to the bot in Telegram instead.")
        path = filedialog.askopenfilename(filetypes=[("Number files", "*.txt *.csv"), ("All", "*.*")])
        if not path:
            return
        try:
            svcs = json.load(open(DB, encoding="utf-8")).get("services") or []
        except Exception:
            svcs = []
        svcs = svcs or ["WHATSAPP", "TELEGRAM", "FACEBOOK", "INSTAGRAM", "TIKTOK"]
        sid = (simpledialog.askstring("Service", "Service for these numbers:\n" + ", ".join(svcs)) or "").strip().upper()
        if sid not in svcs:
            return self.write("Cancelled: service name not recognised.")
        raw = open(path, encoding="utf-8", errors="ignore").read()
        nums = []
        for line in raw.splitlines():
            for field in re.split(r"[,;\t]", line):
                f = field.strip().strip('"')
                if re.fullmatch(r"\+?[\d\s-]{8,18}", f):
                    nums.append(re.sub(r"\D", "", f)); break
        d = {"users": {}, "pool": [], "pools": {}, "withdraws": {}, "wd_seq": 0}
        if os.path.exists(DB):
            d.update(json.load(open(DB, encoding="utf-8")))
        d.setdefault("pools", {})
        pool = d["pools"].setdefault(sid, [])
        have, added = set(pool), 0
        for n in nums:
            if 7 <= len(n) <= 15 and n not in have:
                pool.append(n); have.add(n); added += 1
        json.dump(d, open(DB, "w", encoding="utf-8"), ensure_ascii=False)
        self.write(f"Added {added} numbers to {sid}. {sid} pool: {len(pool)}")

    def install(self):
        self.write("Installing libraries...")
        def run():
            p = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=BASE,
                               capture_output=True, text=True)
            self.q.put("Install finished." if p.returncode == 0 else "Install failed:\n" + p.stdout[-800:] + p.stderr[-800:])
        threading.Thread(target=run, daemon=True).start()

    def on_close(self):
        self.stop_bot(); self.destroy()

if __name__ == "__main__":
    App().mainloop()
