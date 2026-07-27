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

Build it once (the image is tiny and has no build-time dependencies):

```sh
docker build -t ipgeo-community-updater docker/community-updater/
```

```yaml
services:
  ipgeo-updater:
    image: ipgeo-community-updater
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
docker run --rm -v ipgeo-data:/data -e RUN_ONCE=1 ipgeo-community-updater
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
- **Build it yourself — there is no published image to pull.** The build is a two-line
  Dockerfile over `alpine` with no build-time dependencies, so `docker build` takes seconds and
  gives you a ~23 MB image. The source is right here, which also means you can read exactly what
  you are running before you run it.
- **Why no registry image?** The publish workflow
  ([`publish-updater.yml`](../../.github/workflows/publish-updater.yml)) does build and push to
  GHCR, keylessly, using the built-in `GITHUB_TOKEN`. But this organisation's package policy
  permits private packages only, so the pushed image cannot be made public and an anonymous
  `docker pull` gets `denied`. Rather than document a command that fails for you, the quickstart
  builds from source. Docker Hub is not published either — that needs a long-lived account
  credential.
- The image does **not** contain the database — it downloads it at runtime — so it is rebuilt
  only when this directory changes, not on every weekly data release.
- `Dockerfile`, `update.sh`, and `ATTRIBUTION.txt` here are kept **byte-identical** to
  `docker/community-updater/` in the private source repo, so drift is a plain `diff`. This is
  the copy the published image is built from.
