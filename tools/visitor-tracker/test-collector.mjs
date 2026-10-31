import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('collector/worker/index.js', import.meta.url), 'utf8');
const worker = (await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))).default;
const ORIGIN = 'https://chrisrcorona5.github.io';

function database() {
  const db = new DatabaseSync(':memory:');
  db.exec(readFileSync(new URL('collector/drizzle/0000_visitors.sql', import.meta.url), 'utf8'));
  return { prepare(sql) {
    let args = [];
    const statement = {
      bind(...values) { args = values; return statement; },
      async run() { return { results: db.prepare(sql).all(...args) }; },
      async first() { return db.prepare(sql).get(...args) || null; },
      async all() { return { results: db.prepare(sql).all(...args) }; }
    };
    return statement;
  }, async batch(statements) { return Promise.all(statements.map(s => s.all())); } };
}

function setup() {
  const env = { DB: database(), ADMIN_TOKEN: 'test-admin-secret', HASH_SECRET: 'test-hash-secret' };
  async function request(path, { body, admin = false, ip = '203.0.113.10', origin = ORIGIN, headers = {} } = {}) {
    return worker.fetch(new Request('https://collector.test' + path, {
      method: body !== undefined ? 'POST' : 'GET',
      headers: { Origin: origin, 'CF-Connecting-IP': ip, 'User-Agent': 'Mozilla/5.0 Firefox/130',
        ...(admin ? { Authorization: 'Bearer test-admin-secret' } : {}), ...headers },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {})
    }), env);
  }
  return { request, async status() { return (await request('/admin/status', { admin: true })).json(); } };
}

test('new browsers count once across repeated and concurrent opens', async () => {
  const t = setup();
  const visitor = crypto.randomUUID();
  const results = await Promise.all(Array.from({ length: 6 }, () => t.request('/v1/visit', { body: { visitor } })));
  assert.ok(results.every(r => r.status === 204));
  const s = await t.status();
  assert.equal(s.total, 1);
  assert.equal(s.events.length, 1);
  assert.equal(s.recent[0].visits, 1);
  assert.equal(JSON.stringify(s).includes(visitor), false);
});

test('home network excluded and authenticated test visitor bypass is labeled', async () => {
  const t = setup();
  assert.equal((await t.request('/admin/heartbeat', { body: {}, admin: true })).status, 200);
  await t.request('/v1/visit', { body: { visitor: crypto.randomUUID() } });
  assert.equal((await t.status()).total, 0);
  const visitor = crypto.randomUUID();
  await t.request('/admin/test-visitor', { body: { visitor }, admin: true });
  await t.request('/v1/visit', { body: { visitor } });
  const s = await t.status();
  assert.equal(s.total, 0);
  assert.equal(s.tests, 1);
  assert.equal(s.events[0].is_test, 1);
  // A different network can register a real visitor.
  await t.request('/v1/visit', { body: { visitor: crypto.randomUUID() }, ip: '198.51.100.10' });
  assert.equal((await t.status()).total, 1);
});

test('admin access, origin, privacy signals, previews, and malformed bodies', async () => {
  const t = setup();
  assert.equal((await t.request('/admin/status')).status, 401);
  assert.equal((await t.request('/admin/heartbeat', { body: {} })).status, 401);
  const visitor = crypto.randomUUID();
  assert.equal((await t.request('/v1/visit', { body: { visitor }, origin: 'https://attacker.test' })).status, 403);
  for (const headers of [{ DNT: '1' }, { 'Sec-GPC': '1' }, { 'User-Agent': 'Slackbot-LinkExpanding' }]) {
    assert.equal((await t.request('/v1/visit', { body: { visitor }, headers })).status, 204);
  }
  assert.equal((await t.request('/v1/visit', { body: { visitor: 'invalid' } })).status, 400);
  assert.equal((await t.request('/v1/visit', { body: { visitor, junk: 'a'.repeat(1200) } })).status, 400);
  assert.equal((await t.status()).total, 0);
});

test('paged event feed preserves the cursor through duplicate sequence gaps', async () => {
  const t = setup();
  const a = crypto.randomUUID(), b = crypto.randomUUID();
  await t.request('/v1/visit', { body: { visitor: a } });
  await t.request('/v1/visit', { body: { visitor: a } });
  await t.request('/v1/visit', { body: { visitor: b } });
  const initial = await t.status();
  const after = await (await t.request('/admin/status?after=' + initial.events[0].seq, { admin: true })).json();
  assert.equal(after.events.length, 1);
  assert.equal(after.events[0].seq, initial.events[1].seq);
});

const client = readFileSync(new URL('../../assets/js/visitor-counter.js', import.meta.url), 'utf8');
function browser(storage = new Map(), navigator = {}, options = {}) {
  const requests = [];
  const document = { currentScript: { dataset: { endpoint: 'https://collector.test' } },
    visibilityState: 'visible', addEventListener() {}, removeEventListener() {} };
  vm.runInNewContext(client, { document, location: { hostname: options.hostname || 'chrisrcorona5.github.io' },
    navigator, localStorage: { getItem: k => storage.get(k), setItem: (k, v) => storage.set(k, v) },
    crypto, setTimeout: callback => callback(), fetch: (...args) => { requests.push(args); return Promise.resolve(); } });
  return requests;
}

test('client reuses its anonymous browser ID and sends no URL or personal data', () => {
  const storage = new Map();
  const first = browser(storage), second = browser(storage);
  assert.equal(first.length, 1);
  assert.deepEqual(JSON.parse(first[0][1].body), JSON.parse(second[0][1].body));
  assert.deepEqual(Object.keys(JSON.parse(first[0][1].body)), ['visitor']);
});

test('excluded browsers, privacy signals, and localhost never send requests', () => {
  assert.equal(browser(new Map([['portfolio.exclude', '1']])).length, 0);
  assert.equal(browser(new Map(), { doNotTrack: '1' }).length, 0);
  assert.equal(browser(new Map(), { globalPrivacyControl: true }).length, 0);
  assert.equal(browser(new Map(), {}, { hostname: 'localhost' }).length, 0);
});
