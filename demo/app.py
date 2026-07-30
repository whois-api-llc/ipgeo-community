#!/usr/bin/env python3
"""ipgeo Community Edition — tiny self-hostable IP-lookup demo.

One file, stdlib + maxminddb. Looks any IP up against the free community MMDB
and shows whichever fields the record carries (incl. is_vpn / is_datacenter /
ip_type). FIELDS below is the full schema, so it also covers the columns that
are reserved-but-unpopulated today (country_name, is_proxy) — those simply
never render, because absent fields are skipped.

    pip install maxminddb
    IPGEO_MMDB=/path/to/ipgeo-community.mmdb python3 app.py   # http://localhost:8080

Endpoints: `/` (HTML, defaults to the caller's IP) · `/api/lookup?ip=1.1.1.1` (JSON).
Pair with the keep-updated cron or the docker sidecar for weekly freshness.
"""

from __future__ import annotations

import html
import ipaddress
import json
import os
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import maxminddb

MMDB_PATH = os.environ.get("IPGEO_MMDB", "ipgeo-community.mmdb")
PORT = int(os.environ.get("PORT", "8080"))
UPGRADE_URL = (
    "https://ip-geolocation.whoisxmlapi.com/?utm_source=ipgeo-community&utm_medium=demo-tool&utm_campaign=community-launch"
)

FIELDS = [
    "country_code",
    "country_name",
    "region",
    "city",
    "postal_code",
    "latitude",
    "longitude",
    "timezone",
    "asn",
    "as_org",
    "is_vpn",
    "is_proxy",
    "is_datacenter",
    "ip_type",
]

_reader = None
_reader_key: tuple[int, float] | None = None
_reader_checked = 0.0
_STAT_INTERVAL = 60.0  # seconds between freshness stats


def get_reader():
    """Open the MMDB, reopening it when the file is swapped underneath us.

    The updater sidecar replaces the database weekly via atomic rename; a
    memory-mapped reader would otherwise serve the original file forever (and
    the page advertises weekly freshness). Stat at most once a minute.
    """
    global _reader, _reader_key, _reader_checked
    now = time.monotonic()
    if _reader is not None and now - _reader_checked < _STAT_INTERVAL:
        return _reader
    _reader_checked = now
    try:
        st = os.stat(MMDB_PATH)
        key = (st.st_ino, st.st_mtime)
    except OSError:
        if _reader is not None:
            return _reader  # keep serving the open handle if the path vanishes
        raise
    if _reader is None or key != _reader_key:
        new = maxminddb.open_database(MMDB_PATH)
        old, _reader, _reader_key = _reader, new, key
        if old is not None:
            old.close()
    return _reader


def parse_ip(raw: str) -> str | None:
    """Canonical IP string, or None if raw isn't an IP (never echo raw input)."""
    try:
        return str(ipaddress.ip_address(raw.strip()))
    except ValueError:
        return None


def lookup(reader, ip: str) -> dict:
    """Ordered {field: value} for every known field; absent-when-unknown."""
    rec = reader.get(ip) or {}
    return {f: rec[f] for f in FIELDS if rec.get(f) is not None}


def render_page(ip: str | None, result: dict | None, error: str | None = None) -> str:
    rows = ""
    if result is not None:
        if result:
            rows = "".join(
                f"<tr><td><code>{html.escape(k)}</code></td>"
                f"<td>{html.escape(json.dumps(v) if not isinstance(v, str) else v)}</td></tr>"
                for k, v in result.items()
            )
        else:
            rows = '<tr><td colspan="2">No record for this IP (fields are absent when unknown).</td></tr>'
    return f"""<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ipgeo Community — IP lookup</title>
<style>
 body{{font:16px/1.5 system-ui,sans-serif;max-width:640px;margin:3rem auto;padding:0 1rem;color:#1a1a1a}}
 input{{font:inherit;padding:.4rem .6rem;width:14rem}} button{{font:inherit;padding:.4rem 1rem}}
 table{{border-collapse:collapse;margin:1.5rem 0;width:100%}}
 td{{border:1px solid #ddd;padding:.35rem .6rem;word-break:break-all}}
 .cta{{background:#f5f5f5;padding:1rem;border-radius:6px;margin-top:2rem}}
 .err{{color:#b00020}} footer{{font-size:.8rem;color:#666;margin-top:2rem}}
</style>
<h1>ipgeo Community — IP lookup</h1>
<p>Free weekly IP geolocation with <code>is_vpn</code> / <code>is_datacenter</code> flags
and <code>ip_type</code>. No signup.</p>
<form method="get" action="/">
  <input name="ip" placeholder="8.8.8.8 or 2001:db8::1" value="{html.escape(ip or "")}">
  <button>Look up</button>
</form>
{f'<p class="err">{html.escape(error)}</p>' if error else ""}
{f"<table>{rows}</table>" if rows else ""}
<div class="cta">Need <strong>per-IP (/32) precision, daily updates, or confidence
scores</strong>? That's the commercial tier:
<a href="{UPGRADE_URL}">WhoisXML API IP Geolocation</a>. The free database is
ASN/network-block granularity, refreshed weekly.</div>
<footer>Data: <a href="https://github.com/whois-api-llc/ipgeo-community">ipgeo Community
Edition</a> (CC BY-SA 4.0) — flags are network-level, not a judgment about any
individual. Self-host this page: <code>demo/</code> in the repo.
<br>Includes <a href="https://db-ip.com">IP Geolocation by DB-IP</a> (CC BY 4.0).</footer>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "ipgeo-demo/1.0"
    sys_version = ""  # don't advertise the Python patch version publicly
    timeout = 15  # bound half-open connections (thread-per-connection server)

    def _client_ip(self) -> str:
        fwd = self.headers.get("X-Forwarded-For", "")
        first = fwd.split(",")[0].strip() if fwd else ""
        return first or self.client_address[0]

    def _send(self, code: int, body: bytes, ctype: str, head: bool = False) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def do_GET(self) -> None:  # http.server API name
        try:
            self._route()
        except Exception:  # never drop the connection without a status
            traceback.print_exc()  # detail stays server-side
            self._send(500, b"lookup failed", "text/plain")

    def do_HEAD(self) -> None:  # health checks / monitors default to HEAD
        try:
            self._route(head=True)
        except Exception:
            traceback.print_exc()
            self._send(500, b"", "text/plain", head=True)

    def _route(self, head: bool = False) -> None:
        u = urlparse(self.path)
        q = parse_qs(u.query)
        raw = (q.get("ip") or [""])[0]

        if head:
            code = 200 if u.path in ("/", "/api/lookup") else 404
            self._send(code, b"", "text/html; charset=utf-8", head=True)
        elif u.path == "/api/lookup":
            ip = parse_ip(raw)
            if not ip:
                self._send(400, b'{"error":"invalid or missing ip parameter"}', "application/json")
                return
            body = json.dumps({"ip": ip, "record": lookup(get_reader(), ip)}).encode()
            self._send(200, body, "application/json")
        elif u.path == "/":
            ip = parse_ip(raw) if raw else parse_ip(self._client_ip())
            if raw and not ip:
                page = render_page(None, None, error="That doesn't look like an IP address.")
            else:
                page = render_page(ip, lookup(get_reader(), ip) if ip else None)
            self._send(200, page.encode(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, fmt, *args):  # quiet: no per-request access log
        pass


if __name__ == "__main__":
    get_reader()  # fail fast if the MMDB is missing
    print(f"ipgeo demo on http://0.0.0.0:{PORT} (db: {MMDB_PATH})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
