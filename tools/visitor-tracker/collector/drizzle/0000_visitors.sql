CREATE TABLE visitors (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  visitor_hash TEXT NOT NULL UNIQUE,
  first_seen INTEGER NOT NULL,
  last_seen INTEGER NOT NULL,
  visits INTEGER NOT NULL DEFAULT 1,
  is_test INTEGER NOT NULL DEFAULT 0
);
--> statement-breakpoint
CREATE INDEX visitors_first_seen ON visitors(first_seen);
--> statement-breakpoint
CREATE TABLE owner_networks (
  ip_hash TEXT PRIMARY KEY NOT NULL,
  expires INTEGER NOT NULL
);
--> statement-breakpoint
CREATE TABLE test_visitors (
  visitor_hash TEXT PRIMARY KEY NOT NULL,
  expires INTEGER NOT NULL
);
--> statement-breakpoint
CREATE TABLE rate_limits (
  ip_hash TEXT NOT NULL,
  window INTEGER NOT NULL,
  requests INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (ip_hash, window)
);
