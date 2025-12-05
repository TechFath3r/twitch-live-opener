🎮🔔 Twitch Live Opener

A lightweight Windows tool that automatically opens a Twitch stream the moment your favourite streamer goes live — with tray icon controls, logging, and simple setup.

This app runs silently in the background.
The instant a monitored Twitch channel goes offline → LIVE, your browser opens automatically so you never miss a moment.

✨ Features

🔍 Monitors any Twitch channel using the official Twitch API

🚀 Opens the stream instantly when they go live

🟣 System tray icon with a “Quit” option

📝 Rotating log file (twitch_live_opener.log)

🤫 Silent background operation

⚙️ Customisable polling interval

🔐 Uses a .env file for secrets (never committed to Git)

🪟 Optional Windows startup automation via Task Scheduler

🔧 Includes a simple batch launcher for convenience

🚀 Quick Start
1. Clone the repository
git clone https://github.com/techfath3r/twitch-live-opener.git
cd twitch-live-opener

2. Create a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate

3. Install dependencies

If you have a requirements.txt:

pip install -r requirements.txt


Otherwise:

pip install requests python-dotenv pystray pillow

🔧 Configuration

Create a file named .env in the project root:

TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_STREAMER_LOGIN=streamername
POLL_INTERVAL=180

⭐ How to get Twitch API credentials

Go to https://dev.twitch.tv/console/apps

Create a new application

Copy the Client ID

Generate a Client Secret

Redirect URL can be anything (e.g. http://localhost)

Paste both values into your .env file

▶️ Running the Script
Manual run
python twitch_live_opener.py


A tray icon will appear

Logging starts automatically

The script keeps checking for your streamer going live

Using the included batch file

Double-click:

run_twitch_bot.bat


This ensures:

You start in the correct working directory

.env and log files load reliably

Tray icon + logging behave correctly

🟣 System Tray Icon

When running, a tray icon appears near the Windows clock:

✔ Right-click → Quit cleanly shuts down the watcher

✔ Tray thread and watcher loop end gracefully

✔ Log records shutdown events

This makes it feel like a “real app” rather than a bare script.

📝 Logging

All logs are written to:

twitch_live_opener.log

Logged events include:

App startup

Twitch token requests & refreshes

Online/offline detection

When the browser is opened

Errors or connect issues

Tray icon quit events

The logger automatically rotates log files (up to 3 backups).

💡 Auto-Start on Windows (Optional)

Use Task Scheduler for a clean autorun experience.

1. Example run_twitch_bot.bat
@echo off
cd /d "C:\Users\Dan\PycharmProjects\twitch_live_opener.py"
"C:\Users\Dan\PycharmProjects\twitch_live_opener.py\.venv\Scripts\python.exe" twitch_live_opener.py

2. Create a Task Scheduler entry

Open Task Scheduler

Click Create Task

Triggers

At log on

On workstation unlock (optional)

Action

Start a program

Program/script: path to run_twitch_bot.bat

Start in: your project folder

Save and you're done

Your watcher now launches automatically whenever Windows starts or wakes.

📂 Project Structure
twitch-live-opener/
│
├─ twitch_live_opener.py        # main script
├─ run_twitch_bot.bat           # optional launcher
├─ .gitignore                   # ensures secrets & IDE files aren't committed
├─ .env                         # your Twitch secrets (ignored by Git)
├─ twitch_live_opener.log       # rotating log file
└─ .venv/                       # virtual environment (ignored)

🔐 Security Notes

Never commit your .env file

.gitignore already protects:

secrets

logs

venv

PyCharm config

Treat your Twitch Client Secret like a password

📜 License

MIT License (recommended).
Add a LICENSE file such as:

MIT License © 2025 Your Name

🤝 Contributing

Pull Requests are welcome!
If you'd like to add features (notifications, GUI config, multi-streamer support), feel free to open an issue.

⭐ If you find this useful

Please give the repo a star — it helps others discover it!