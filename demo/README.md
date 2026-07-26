# ipgeo Community — IP lookup demo

A one-file web app that looks any IP up against the free
[ipgeo Community Edition](https://github.com/whois-api-llc/ipgeo-community) database and
shows every field — geolocation plus `is_vpn` / `is_proxy` / `is_datacenter` / `ip_type`.
Stdlib + `maxminddb`, no framework, no account, no telemetry.

## Run it

```sh
pip install maxminddb
curl -fsSLO https://github.com/whois-api-llc/ipgeo-community/releases/latest/download/ipgeo-community.mmdb
python3 app.py            # http://localhost:8080
```

- `/` — HTML lookup (defaults to your IP; honors the first `X-Forwarded-For` hop behind a proxy)
- `/api/lookup?ip=8.8.8.8` — JSON

Config: `IPGEO_MMDB` (default `./ipgeo-community.mmdb`), `PORT` (default `8080`).

## Docker

```sh
docker build -t ipgeo-demo .
docker run -p 8080:8080 -v ipgeo-data:/data -e IPGEO_MMDB=/data/ipgeo-community.mmdb ipgeo-demo
```

Share the `ipgeo-data` volume with the
[community-updater sidecar](https://github.com/whois-api-llc/ipgeo-community/tree/main/docker/community-updater) and the database refreshes
weekly with no further care. The app re-stats the database once a minute and reopens it automatically after
the sidecar swaps in a new file — no restart needed.

## Notes

- `http.server` is fine for a demo, but put a real reverse proxy (nginx/Caddy/Cloudflare)
  in front of any public deployment — connections are bounded by a 15s timeout, not by a
  connection limit.
- Fields are **absent when unknown** — the page says so instead of inventing blanks.
- Flags are **ASN/network-block granularity** (the free tier's design): a flagged range
  describes infrastructure, not a judgment about an individual address. Per-IP precision,
  daily updates, and confidence scores are the commercial tier (CTA in the page footer).
- Database license: **CC BY-SA 4.0** — keep `ATTRIBUTION.txt` with redistributed copies.
