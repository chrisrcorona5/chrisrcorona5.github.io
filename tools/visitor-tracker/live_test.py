#!/usr/bin/env python3
"""Exercise the published portfolio using labeled test visitors, never real counts."""
import json
from pathlib import Path
import sqlite3
import subprocess
import time
import uuid
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

SITE = "https://chrisrcorona5.github.io/"
config = json.loads((Path.home() / ".config/portfolio-tracker/config.json").read_text())
database = Path.home() / ".local/state/portfolio-tracker/state.sqlite3"


def api(path, body=None):
    req = Request(config["endpoint"] + path,
                  data=json.dumps(body).encode() if body is not None else None,
                  headers={"Authorization": "Bearer " + config["admin_token"], "Content-Type": "application/json", "User-Agent": "PortfolioDesktop/1.0"})
    with urlopen(req, timeout=15) as response:
        return json.load(response)


def wait_delivered(seq):
    deadline = time.monotonic() + 50
    while time.monotonic() < deadline:
        with sqlite3.connect(database) as db:
            row = db.execute("SELECT notified FROM events WHERE seq=?", (seq,)).fetchone()
        if row and row[0]:
            return
        time.sleep(1)
    raise AssertionError("Desktop did not deliver the test notification")


def open_visitor(browser, visitor):
    context = browser.new_context()
    context.add_init_script("if(location.origin==='https://chrisrcorona5.github.io')localStorage.setItem('portfolio.visitor'," + json.dumps(visitor) + ");")
    page = context.new_page()
    with page.expect_response(lambda r: r.url == config["endpoint"] + "/v1/visit", timeout=20000) as received:
        page.goto(SITE, wait_until="domcontentloaded")
    assert received.value.status == 204, received.value.status
    return context, page


def main():
    api("/admin/heartbeat", {})
    before = api("/admin/status")
    monitor = subprocess.Popen([
        "dbus-monitor", "--session",
        "type='method_call',interface='org.freedesktop.Notifications',member='Notify',arg0='Portfolio Tracker'"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Owner browser flag prevents even a request to the collector.
            context = browser.new_context()
            context.add_init_script("if(location.origin==='https://chrisrcorona5.github.io')localStorage.setItem('portfolio.exclude','1');")
            page = context.new_page()
            sent = []
            page.on("request", lambda r: sent.append(r.url) if r.url.startswith(config["endpoint"]) else None)
            page.goto(SITE, wait_until="domcontentloaded")
            page.wait_for_function("!!document.querySelector('script[src*=\"visitor-counter.js\"]')")
            page.wait_for_timeout(2000)
            assert not sent, sent
            context.close()
            print("PASS: owner browser opens the exact public URL without sending tracking requests", flush=True)

            # Fresh browser on the owner's connection is excluded server-side.
            context, _ = open_visitor(browser, str(uuid.uuid4()))
            context.close()
            assert api("/admin/status")["latest_seq"] == before["latest_seq"]
            print("PASS: unmarked browser on the registered home connection is also excluded", flush=True)

            visitor = str(uuid.uuid4())
            api("/admin/test-visitor", {"visitor": visitor})
            context, page = open_visitor(browser, visitor)
            after = api("/admin/status")
            seq = after["latest_seq"]
            assert after["tests"] == before["tests"] + 1
            assert after["total"] == before["total"]
            with page.expect_response(lambda r: r.url == config["endpoint"] + "/v1/visit"):
                page.reload(wait_until="domcontentloaded")
            assert api("/admin/status")["tests"] == after["tests"]
            wait_delivered(seq)
            context.close()
            print("PASS: simulated new visitor sends a real visit from the public URL, notifies Linux, and reload deduplicates", flush=True)

            # Model sleep/recovery by stopping only our own notification service.
            subprocess.run(["systemctl", "--user", "stop", "portfolio-tracker.service"], check=True)
            try:
                visitor = str(uuid.uuid4())
                api("/admin/test-visitor", {"visitor": visitor})
                context, _ = open_visitor(browser, visitor)
                context.close()
                backlog = api("/admin/status")
                assert backlog["tests"] == after["tests"] + 1
            finally:
                subprocess.run(["systemctl", "--user", "start", "portfolio-tracker.service"], check=True)
            wait_delivered(backlog["latest_seq"])
            browser.close()
            print("PASS: cloud records visits while desktop service is stopped; restart retrieves and notifies", flush=True)
    finally:
        monitor.terminate()
        captured, _ = monitor.communicate(timeout=5)
    assert '[Test] New portfolio visitor' in captured, "No matching Linux notification observed on D-Bus"
    print("PASS: actual org.freedesktop.Notifications.Notify calls observed; real totals unchanged", flush=True)


if __name__ == "__main__":
    main()
