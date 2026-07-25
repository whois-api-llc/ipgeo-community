# ipgeo-community-updater — keyless MMDB refresh sidecar

A tiny container (~25 MB) that keeps the free
[ipgeo Community Edition](https://github.com/whois-api-llc/ipgeo-community) database fresh in a
shared volume — a **keyless drop-in for the `geoipupdate` sidecar pattern**: no account, no license
key, no env secrets. It downloads the weekly MMDB from GitHub Releases, verifies the SHA-256
against `MANIFEST.json`, swaps atomically (readers never see a torn file), no-ops when nothing
changed, and keeps `ATTRIBUTION.txt` next to the data (CC BY-SA 4.0 — the notice travels with it).

The **data cadence is weekly (Mondays)** — the default daily check exists only to pick a new
release up promptly; the other six days it's a no-op.

## Compose sidecar

```yaml
services:
  ipgeo-updater:
    image: ghcr.io/whois-api-llc/ipgeo-community-updater:latest
    volumes:
      - ipgeo-data:/data
    restart: unless-stopped

  app:
    image: your-app
    volumes:
      - ipgeo-data:/data:ro # read /data/ipgeo-community.mmdb; reopen the reader after updates

volumes:
  ipgeo-data:
```

## One-shot / cron mode

```sh
docker run --rm -v ipgeo-data:/data -e RUN_ONCE=1 ghcr.io/whois-api-llc/ipgeo-community-updater
```

Exit 0 = up to date or updated; exit 1 = fetch/verify failed (current DB left untouched).

## Configuration

| Env                     | Default                               | Meaning                                            |
| ----------------------- | ------------------------------------- | -------------------------------------------------- |
| `DEST`                  | `/data`                               | Where the MMDB + MANIFEST + ATTRIBUTION land       |
| `UPDATE_INTERVAL_HOURS` | `24`                                  | Check interval (releases are weekly; checks no-op) |
| `RETRY_MINUTES`         | `60`                                  | Backoff after a failed fetch/verify                |
| `RUN_ONCE`              | `0`                                   | `1` = single update pass, then exit                |
| `BASE`                  | GitHub `releases/latest/download` URL | Override for mirrors/testing                       |

## Notes

- Long-running readers memory-map the file: reopen after a swap (or use e.g.
  `ngx_http_geoip2_module`'s `auto_reload`).
- The database is **CC BY-SA 4.0** — keep the attribution files with redistributed copies. Need
  per-IP precision, daily updates, or confidence scores? That's the commercial
  [WhoisXML / Panavision](https://www.whoisxmlapi.com/?utm_source=ipgeo-community&utm_medium=container&utm_campaign=community-launch)
  tier.
- **Images:** published to GHCR as `ghcr.io/whois-api-llc/ipgeo-community-updater`, tagged
  `latest` and `sha-<commit>`, for `linux/amd64` and `linux/arm64`. Published by
  [`publish-updater.yml`](../../.github/workflows/publish-updater.yml) using the built-in
  `GITHUB_TOKEN` — no registry credential is stored anywhere. **Docker Hub is not published**
  (it needs a long-lived account credential); pull from GHCR, or build locally:
  `docker build -t ipgeo-community-updater docker/community-updater/`.
- The image does **not** contain the database — it downloads it at runtime — so it is rebuilt
  only when this directory changes, not on every weekly data release.
- `Dockerfile`, `update.sh`, and `ATTRIBUTION.txt` here are kept **byte-identical** to
  `docker/community-updater/` in the private source repo, so drift is a plain `diff`. This is
  the copy the published image is built from.
