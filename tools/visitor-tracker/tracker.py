#!/usr/bin/env python3
"""Private local dashboard, durable sync, and Linux desktop notifications."""
import argparse
import json
import logging
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CONFIG = Path.home() / ".config/portfolio-tracker/config.json"
STATE = Path.home() / ".local/state/portfolio-tracker/state.sqlite3"
LOG = logging.getLogger("portfolio-tracker")


class Tracker:
    def __init__(self, config_path=CONFIG, state_path=STATE):
        self.config = json.loads(Path(config_path).read_text())
        self.endpoint = self.config["endpoint"].rstrip("/")
        if urlparse(self.endpoint).scheme != "https":
            raise ValueError("The collector must use HTTPS")
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        self.last_heartbeat = 0
        self.stop = threading.Event()
        self.poll_lock = threading.Lock()
        with self.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(
                    seq INTEGER PRIMARY KEY, first_seen INTEGER NOT NULL,
                    is_test INTEGER NOT NULL, notified INTEGER NOT NULL DEFAULT 0);
            """)
        self.state_path.chmod(0o600)

    def db(self):
        return sqlite3.connect(self.state_path, timeout=10)

    def setting(self, key, default=None):
        with self.db() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    @staticmethod
    def put(db, key, value):
        db.execute("INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))

    def request(self, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(self.endpoint + path, data=data, headers={
            "Authorization": "Bearer " + self.config["admin_token"],
            "Content-Type": "application/json", "User-Agent": "PortfolioDesktop/1.0"
        })
        with urlopen(req, timeout=12) as reply:
            # Bound memory consumption even if the upstream is misconfigured.
            raw = reply.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("Collector response too large")
            return json.loads(raw)

    def sync(self):
        with self.poll_lock:
            # Register the current home connection before pulling any events.
            if time.monotonic() - self.last_heartbeat >= 60:
                self.request("/admin/heartbeat", {})
                self.last_heartbeat = time.monotonic()
            after = self.setting("cursor", 0)
            # Drain backlog in bounded pages; never jump to the server's latest ID.
            for _ in range(20):
                payload = self.request("/admin/status?after=" + str(after))
                events = payload.get("events", [])
                with self.db() as db:
                    for event in events:
                        db.execute("INSERT OR IGNORE INTO events(seq, first_seen, is_test) VALUES (?,?,?)",
                                   (event["seq"], event["first_seen"], event["is_test"]))
                        after = max(after, event["seq"])
                    self.put(db, "cursor", after)
                    self.put(db, "snapshot", payload)
                    self.put(db, "last_sync", int(time.time()))
                    self.put(db, "last_error", None)
                if len(events) < 100:
                    break

    def notify(self, title, body):
        env = os.environ.copy()
        env.setdefault("DBUS_SESSION_BUS_ADDRESS", "unix:path=/run/user/" + str(os.getuid()) + "/bus")
        try:
            result = subprocess.run([
                "notify-send", "--print-id", "--app-name=Portfolio Tracker",
                "--icon=network-workgroup", "--expire-time=10000", title, body
            ], env=env, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            LOG.warning("Desktop notifications unavailable; retaining pending alerts")
            return False
        if result.returncode:
            LOG.warning("Desktop notifications unavailable; retaining pending alerts")
            return False
        LOG.info("Delivered notification %s: %s", result.stdout.strip(), title)
        return True

    def deliver_pending(self):
        # Keep test traffic out of the real visitor totals and alert groups.
        for is_test in (0, 1):
            with self.db() as db:
                rows = db.execute("SELECT seq FROM events WHERE notified=0 AND is_test=? ORDER BY seq", (is_test,)).fetchall()
            if not rows:
                continue
            count = len(rows)
            prefix = "[Test] " if is_test else ""
            title = prefix + ("New portfolio visitor" if count == 1 else f"{count} new portfolio visitors")
            snapshot = self.setting("snapshot", {})
            body = f"{count} first-time browser{'s' if count != 1 else ''}. Total real visitors: {snapshot.get('total', 0)}."
            if self.notify(title, body):
                with self.db() as db:
                    db.executemany("UPDATE events SET notified=1 WHERE seq=?", rows)

    def poll_once(self):
        try:
            self.sync()
        except (OSError, ValueError, URLError, sqlite3.Error, KeyError) as exc:
            # Do not log request headers, response bodies, or secrets.
            error = type(exc).__name__
            with self.db() as db:
                self.put(db, "last_error", error)
            LOG.warning("Sync unavailable (%s); retrying automatically", error)
        self.deliver_pending()

    def run(self):
        while not self.stop.is_set():
            self.poll_once()
            self.stop.wait(max(5, int(self.config.get("poll_seconds", 15))))

    def status(self):
        snapshot = self.setting("snapshot", {})
        return {"total": snapshot.get("total", 0), "today": snapshot.get("today", 0),
                "last_24h": snapshot.get("last_24h", 0), "tests": snapshot.get("tests", 0),
                "recent": snapshot.get("recent", []), "last_sync": self.setting("last_sync"),
                "last_error": self.setting("last_error"), "site": "https://chrisrcorona5.github.io/"}


DASHBOARD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Tracker</title>
<style>
:root{font-family:system-ui,sans-serif;color:#e4e9f1;background:#101723;color-scheme:dark}
body{max-width:900px;margin:50px auto;padding:0 24px}h1{font-size:30px;margin-bottom:8px}
p{color:#a7b5ca;line-height:1.6}.cards{display:flex;gap:16px;flex-wrap:wrap;margin:30px 0}
.card{background:#1b2738;border:1px solid #304158;padding:24px;min-width:180px;border-radius:14px;flex:1}
.number{font-size:44px;font-weight:650;margin-bottom:6px}.label{color:#adbed5}table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:14px 10px;border-bottom:1px solid #304158}th{color:#adbed5;font-weight:500}
a{color:#87c6ff}.test{color:#c2a6ec}.small{font-size:14px}.status{color:#88d9ad}button{padding:10px 16px;border-radius:8px;border:1px solid #526780;background:#22344b;cursor:pointer}
</style></head><body>
<p class="small">LOCAL DESKTOP · PRIVATE ANALYTICS</p><h1>Portfolio visitors</h1>
<p>First-time browsers opening <a href="https://chrisrcorona5.github.io/" target="_blank" rel="noreferrer">your portfolio</a>.
Your browsers and current home connection are excluded.</p><p id="status" class="status">Connecting…</p>
<div class="cards"><div class="card"><div id="total" class="number">—</div><div class="label">Unique browsers</div></div>
<div class="card"><div id="day" class="number">—</div><div class="label">New in the last 24 hours</div></div>
<div class="card"><div id="tests" class="number">—</div><div class="label">Test visitors · excluded from totals</div></div></div>
<h2>Recent visitors</h2><table><thead><tr><th>First opened</th><th>Last opened</th><th>Type</th></tr></thead><tbody id="rows"></tbody></table>
<p id="empty">No recorded visitors yet.</p><p class="small">Updates every 10 seconds. Alerts appear only on this Linux desktop.
Cloud collection continues while the desktop sleeps. This counts browsers, not verified people.</p>
<p class="small">Using another browser or device? Open <a href="https://chrisrcorona5.github.io/exclude-visits/" target="_blank" rel="noreferrer">browser exclusion</a>
once in that browser; it immediately returns to the normal portfolio URL. Private browsing and cleared storage reset browser identity.</p>
<script>
const date=t=>new Date(t*1000).toLocaleString();
async function update(){try{const r=await fetch('/api/status',{cache:'no-store'});if(!r.ok)throw Error();const s=await r.json();
document.getElementById('total').textContent=s.total;document.getElementById('day').textContent=s.last_24h;document.getElementById('tests').textContent=s.tests;
const status=document.getElementById('status');const stale=!s.last_sync||Date.now()/1000-s.last_sync>90;
status.textContent=(s.last_error||stale?'Reconnecting automatically':'Connected · notifications enabled')+(s.last_sync?' · Last synced '+date(s.last_sync):'');
status.style.color=s.last_error||stale?'#efc47d':'#88d9ad';const tbody=document.getElementById('rows');tbody.replaceChildren();
for(const e of s.recent){const row=document.createElement('tr');for(const v of [date(e.first_seen),date(e.last_seen),e.is_test?'Test':'Visitor']){const td=document.createElement('td');td.textContent=v;if(e.is_test)td.className='test';row.appendChild(td)}tbody.appendChild(row)}
document.getElementById('empty').hidden=s.recent.length>0;
}catch(e){document.getElementById('status').textContent='Local service unavailable; refresh after it restarts.'}}
update();setInterval(update,10000);
</script></body></html>"""


def dashboard_handler(tracker):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            port = tracker.config.get("port", 8765)
            # Reject DNS rebinding and cross-origin browser requests.
            if self.headers.get("Host") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
                self.send_error(403)
                return
            origin = self.headers.get("Origin")
            if origin and origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
                self.send_error(403)
                return
            if self.path == "/api/status":
                content = json.dumps(tracker.status()).encode()
                content_type = "application/json"
            elif self.path == "/":
                content = DASHBOARD.encode()
                content_type = "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_):
            pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    tracker = Tracker(args.config, args.state)
    if args.status:
        print(json.dumps(tracker.status(), indent=2))
        return
    if args.once:
        tracker.poll_once()
        return
    server = ThreadingHTTPServer(("127.0.0.1", tracker.config.get("port", 8765)), dashboard_handler(tracker))
    thread = threading.Thread(target=tracker.run, daemon=True)
    thread.start()
    def stop(*_):
        tracker.stop.set()
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    LOG.info("Dashboard listening at http://127.0.0.1:%s", server.server_port)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        tracker.stop.set()
        thread.join(timeout=30)
        server.server_close()


if __name__ == "__main__":
    main()
