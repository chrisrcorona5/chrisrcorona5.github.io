const ORIGIN = "https://chrisrcorona5.github.io";
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const BOT = /bot\b|crawler|spider|preview|facebookexternalhit|slackbot|curl\//i;
const encoder = new TextEncoder();

function response(data, status = 200, cors = false) {
  const headers = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Vary": "Origin"
  };
  if (cors) {
    headers["Access-Control-Allow-Origin"] = ORIGIN;
    headers["Access-Control-Allow-Methods"] = "POST, OPTIONS";
    headers["Access-Control-Allow-Headers"] = "Content-Type";
  }
  if (status === 204) return new Response(null, { status, headers });
  headers["Content-Type"] = "application/json";
  return new Response(JSON.stringify(data), { status, headers });
}

async function hash(secret, value) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return Array.from(new Uint8Array(signature), b => b.toString(16).padStart(2, "0")).join("");
}

async function authorized(request, env) {
  const actual = request.headers.get("Authorization") || "";
  const expected = "Bearer " + env.ADMIN_TOKEN;
  // Equal-length digests avoid comparing the raw secret with an early exit.
  const [a, b] = await Promise.all([hash(env.HASH_SECRET, actual), hash(env.HASH_SECRET, expected)]);
  let different = 0;
  for (let i = 0; i < a.length; i++) different |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return different === 0;
}

async function smallJSON(request) {
  if (Number(request.headers.get("Content-Length") || 0) > 1024) throw new Error("body too large");
  const reader = request.body?.getReader();
  if (!reader) throw new Error("missing body");
  let length = 0;
  const chunks = [];
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    length += value.byteLength;
    if (length > 1024) { await reader.cancel(); throw new Error("body too large"); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder().decode(bytes));
}

async function handle(request, env) {
  const url = new URL(request.url);
  const cors = request.headers.get("Origin") === ORIGIN;
  if (url.pathname === "/health" && request.method === "GET") return response({ ok: true });
  if (!env.DB || !env.ADMIN_TOKEN || !env.HASH_SECRET) return response({ error: "unconfigured" }, 503);
  const now = Math.floor(Date.now() / 1000);
  // Only trust the edge's connecting IP. Never accept a client-supplied forwarded IP.
  const ip = request.headers.get("CF-Connecting-IP");
  const ipHash = ip ? await hash(env.HASH_SECRET, "network:" + ip) : null;

  if (url.pathname.startsWith("/admin/")) {
    if (!await authorized(request, env)) return response({ error: "unauthorized" }, 401);
    if (url.pathname === "/admin/heartbeat" && request.method === "POST") {
      if (!ipHash) return response({ error: "edge IP unavailable" }, 503);
      await env.DB.batch([
        env.DB.prepare("INSERT INTO owner_networks(ip_hash, expires) VALUES (?, ?) ON CONFLICT(ip_hash) DO UPDATE SET expires=excluded.expires").bind(ipHash, now + 900),
        env.DB.prepare("DELETE FROM owner_networks WHERE expires < ?").bind(now),
        env.DB.prepare("DELETE FROM test_visitors WHERE expires < ?").bind(now),
        env.DB.prepare("DELETE FROM rate_limits WHERE window < ?").bind(Math.floor(now / 60) - 2)
      ]);
      return response({ excluded: true, expires: now + 900 });
    }
    if (url.pathname === "/admin/test-visitor" && request.method === "POST") {
      let body;
      try { body = await smallJSON(request); } catch (_) { return response({ error: "invalid body" }, 400); }
      if (!UUID.test(body.visitor || "")) return response({ error: "invalid visitor" }, 400);
      const visitorHash = await hash(env.HASH_SECRET, "visitor:" + body.visitor.toLowerCase());
      await env.DB.prepare("INSERT INTO test_visitors(visitor_hash, expires) VALUES (?, ?) ON CONFLICT(visitor_hash) DO UPDATE SET expires=excluded.expires").bind(visitorHash, now + 900).run();
      return response({ registered: true, expires: now + 900 });
    }
    if (url.pathname === "/admin/status" && request.method === "GET") {
      const cursor = Number(url.searchParams.get("after") || 0);
      if (!Number.isSafeInteger(cursor) || cursor < 0) return response({ error: "invalid cursor" }, 400);
      const startToday = Math.floor(now / 86400) * 86400;
      const [totals, events, recent] = await env.DB.batch([
        env.DB.prepare(`SELECT COUNT(CASE WHEN is_test=0 THEN 1 END) AS total,
          COUNT(CASE WHEN is_test=1 THEN 1 END) AS tests,
          COUNT(CASE WHEN is_test=0 AND first_seen>=? THEN 1 END) AS today,
          COUNT(CASE WHEN is_test=0 AND first_seen>=? THEN 1 END) AS last_24h,
          COALESCE(MAX(seq),0) AS latest_seq FROM visitors`).bind(startToday, now - 86400),
        env.DB.prepare("SELECT seq, first_seen, is_test FROM visitors WHERE seq>? ORDER BY seq LIMIT 100").bind(cursor),
        env.DB.prepare("SELECT seq, first_seen, last_seen, visits, is_test FROM visitors ORDER BY seq DESC LIMIT 30")
      ]);
      return response({ ...totals.results[0], events: events.results, recent: recent.results, server_time: now });
    }
    return response({ error: "not found" }, 404);
  }

  if (url.pathname !== "/v1/visit") return response({ error: "not found" }, 404);
  if (!cors) return response({ error: "origin rejected" }, 403);
  if (request.method === "OPTIONS") return response(null, 204, true);
  if (request.method !== "POST") return response({ error: "method rejected" }, 405, true);
  const userAgent = request.headers.get("User-Agent") || "";
  if (!userAgent || BOT.test(userAgent) || request.headers.get("DNT") === "1" || request.headers.get("Sec-GPC") === "1") return response(null, 204, true);
  if (!ipHash) return response({ error: "edge IP unavailable" }, 503, true);
  let body;
  try { body = await smallJSON(request); } catch (_) { return response({ error: "invalid body" }, 400, true); }
  if (!UUID.test(body.visitor || "")) return response({ error: "invalid visitor" }, 400, true);
  const visitorHash = await hash(env.HASH_SECRET, "visitor:" + body.visitor.toLowerCase());
  const [test, owner] = await env.DB.batch([
    env.DB.prepare("SELECT 1 FROM test_visitors WHERE visitor_hash=? AND expires>=?").bind(visitorHash, now),
    env.DB.prepare("SELECT 1 FROM owner_networks WHERE ip_hash=? AND expires>=?").bind(ipHash, now)
  ]);
  const isTest = test.results.length ? 1 : 0;
  if (!isTest && owner.results.length) return response(null, 204, true);
  // Limit write amplification. Browser identity remains the deduplication key.
  const rate = await env.DB.prepare("INSERT INTO rate_limits(ip_hash, window) VALUES (?, ?) ON CONFLICT(ip_hash, window) DO UPDATE SET requests=requests+1 RETURNING requests").bind(ipHash, Math.floor(now / 60)).first();
  if (rate.requests > 120) return response({ error: "rate limited" }, 429, true);
  await env.DB.prepare(`INSERT INTO visitors(visitor_hash, first_seen, last_seen, is_test) VALUES (?, ?, ?, ?)
    ON CONFLICT(visitor_hash) DO UPDATE SET last_seen=excluded.last_seen, visits=visitors.visits+1
    WHERE excluded.last_seen-visitors.last_seen>=10`).bind(visitorHash, now, now, isTest).run();
  // Identical response for first visits, repeats, and excluded owners.
  return response(null, 204, true);
}

export default {
  async fetch(request, env) {
    try { return await handle(request, env); }
    catch (_) { return response({ error: "temporarily unavailable" }, 503, request.headers.get("Origin") === ORIGIN); }
  }
};
