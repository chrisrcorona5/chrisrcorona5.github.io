# Private portfolio visitor tracker

The public URL remains `https://chrisrcorona5.github.io/`. The portfolio has no
visible counter or tracking popup. A small script sends a random browser UUID to
an online collector. The database stores its keyed hash and first/last visit
times, never names, emails, page URLs, query strings, or raw IP addresses in its
application tables. Hosting providers may maintain their own request logs.

## On this Linux desktop

Open **Portfolio Tracker** from the applications menu or desktop, or visit
<http://127.0.0.1:8765/>. The dashboard refreshes every 10 seconds. The notification
service polls every 15 seconds, groups accumulated first visits, and retains
undelivered notifications for retry. Returning browsers do not trigger another
first-visit alert.

The service is enabled at boot through the user systemd manager. User lingering
is already enabled on this machine. It retries network failures and resumes
polling after suspend; the online collector continues recording while the rig is
asleep or off. Stopping the desktop service does not stop cloud collection.

```sh
systemctl --user status portfolio-tracker.service
journalctl --user -u portfolio-tracker.service -n 30
python3 ~/.local/share/portfolio-tracker/tracker.py --status
systemctl --user restart portfolio-tracker.service
```

Private credentials are in `~/.config/portfolio-tracker/config.json` (mode 600).
The local event cursor and notification history live in
`~/.local/state/portfolio-tracker/state.sqlite3`. The dashboard binds only to
loopback and never sends the cloud admin token to a browser. Neither the private
configuration nor local visitor history belongs in Git or the Jekyll output.

Reinstall after modifying `tracker.py`:

```sh
python3 tools/visitor-tracker/install.py
```

## Excluding yourself

The desktop registers its current public connection as excluded every minute,
with a 15-minute expiry. This also excludes other devices/people sharing that
connection while registered. Only a keyed hash of the address is stored.

For persistent exclusion independent of networks, open
<https://chrisrcorona5.github.io/exclude-visits/> **once in each browser/device you
use**. It sets `portfolio.exclude=1` in local storage, then immediately replaces
itself with the ordinary portfolio homepage. The regular link stays unchanged.
This has been opened in the desktop's default browser during setup. The same
action is also available from the private dashboard.

To remove the browser exclusion, run this in the portfolio's developer console:

```js
localStorage.removeItem('portfolio.exclude');
```

To remove the network exclusion, stop the desktop service and wait 15 minutes.
The browser flag remains until explicitly removed or site storage is cleared.

## What the count means

Counts are first-time **browsers**, starting when tracking was enabled. The
browser's random ID persists across visits and network changes. Different devices,
private browsing, or clearing storage can count the same person again. Visitors
with unavailable storage, DNT, Global Privacy Control, or blocked requests are not
counted. Common preview/bot user agents are ignored, but human identification is
not guaranteed. No fingerprinting or attempts to bypass blockers are used.

Every ordinary visitor uses the same public link; this cannot distinguish emailed
visits from organic traffic or identify which email recipient opened it.

## Collector and deployment

The collector runs at
<https://corona-portfolio-visits.zestyemery.chatgpt.site> using the
[Sites skill](/home/ccorona/.codex/plugins/cache/openai-curated-remote/sites/1.1.2/skills/sites/SKILL.md).
The public root intentionally returns 404. `/health` is public; `/v1/visit` accepts
only portfolio-origin submissions. All `/admin/*` endpoints require the private
admin bearer token. Public telemetry submissions are inherently forgeable; an
origin check, input limits, bot filtering and per-network rate limits reduce
accidental/noisy counts but cannot prove a visitor is a human.

The canonical collector code is in `collector/`. Its separate Sites source
checkout and deploy archive are in the Git-ignored `local/visitor-collector/`
and `local/collector.tar.gz`. Copy canonical files to that checkout before
following the Sites skill's source/package/deployment workflow. Preserve its
project ID and `DB` D1 binding; append schema migrations. Runtime secrets
`ADMIN_TOKEN` and `HASH_SECRET` are configured through Sites and excluded from
the source/build. Do not change or rotate `HASH_SECRET` without planning a
migration, since it determines the stored anonymous identities.

To provision on another desktop, securely copy the private config (or supply a
new admin token matched to the collector). Its fields are `endpoint`,
`admin_token`, `port` (8765), and `poll_seconds` (15). Python 3 and `notify-send`
are sufficient to run the service; Node 22+ and Playwright are needed only for
development/testing. Cloud availability and retention are subject to the hosting
provider; this is not an uptime SLA.

## Verification

```sh
node --test tools/visitor-tracker/test-collector.mjs
python3 -m unittest discover -s tools/visitor-tracker -p 'test_*.py' -v
python3 tools/visitor-tracker/live_test.py
```

The live test opens the actual public URL in isolated Chromium contexts, verifies
owner browser/network exclusion, registers labeled test identities, verifies
deduplication, observes Linux notification D-Bus calls, and checks that cloud
visits are retrieved after the local service is restarted. Test visitors bypass
the home-network exclusion only after authenticated registration, expire after
15 minutes, and remain labeled separately from real visitor totals. Test
traffic never increments the real count. This simulates new visitors; it does
not claim to involve actual strangers or physically suspend the computer.
