#!/usr/bin/env python3
"""Install the desktop tracker using an existing private config file."""
from pathlib import Path
import shutil
import subprocess

home = Path.home()
source = Path(__file__).resolve().parent
config = home / ".config/portfolio-tracker/config.json"
if not config.is_file():
    raise SystemExit("Configure ~/.config/portfolio-tracker/config.json before installing (see README).")
config.chmod(0o600)
app = home / ".local/share/portfolio-tracker"
app.mkdir(parents=True, exist_ok=True)
shutil.copy2(source / "tracker.py", app / "tracker.py")
units = home / ".config/systemd/user"
units.mkdir(parents=True, exist_ok=True)
(units / "portfolio-tracker.service").write_text("""[Unit]
Description=Portfolio visitor counter and desktop notifications
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/.local/share/portfolio-tracker/tracker.py
Restart=always
RestartSec=10
TimeoutStopSec=35
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=%h/.local/state/portfolio-tracker

[Install]
WantedBy=default.target
""")
(home / ".local/state/portfolio-tracker").mkdir(parents=True, mode=0o700, exist_ok=True)
applications = home / ".local/share/applications"
applications.mkdir(parents=True, exist_ok=True)
desktop = """[Desktop Entry]
Type=Application
Name=Portfolio Tracker
Comment=Private website visitor counts and Linux notifications
Exec=xdg-open http://127.0.0.1:8765/
Icon=network-workgroup
Terminal=false
Categories=Network;Utility;
"""
(applications / "portfolio-tracker.desktop").write_text(desktop)
# Keep a convenient desktop launcher as well as the application menu entry.
desktop_folder = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True).stdout.strip()
if desktop_folder and Path(desktop_folder).is_dir():
    launcher = Path(desktop_folder) / "Portfolio Tracker.desktop"
    launcher.write_text(desktop)
    launcher.chmod(0o755)
subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
subprocess.run(["systemctl", "--user", "enable", "portfolio-tracker.service"], check=True)
subprocess.run(["systemctl", "--user", "restart", "portfolio-tracker.service"], check=True)
print("Installed and enabled Portfolio Tracker: http://127.0.0.1:8765/")
