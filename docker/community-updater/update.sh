#!/bin/sh
# ipgeo Community Edition refresh sidecar — a keyless geoipupdate drop-in.
# Downloads the free weekly MMDB into $DEST (a shared volume), verifies its
# sha256 against MANIFEST.json, swaps atomically, and no-ops when unchanged.
# The DATA cadence is weekly (Mondays); the default daily check just notices
# a new release promptly and does nothing the other six days.
set -eu

DEST="${DEST:-/data}"
# Normalize to absolute ONCE. update() cd's into $DEST on every pass, so a
# relative override would descend a level per pass (data, data/data, …) —
# still reporting success while the shared volume goes stale after the first.
case "$DEST" in /*) ;; *) DEST="$PWD/$DEST" ;; esac
BASE="${BASE:-https://github.com/whois-api-llc/ipgeo-community/releases/latest/download}"
UPDATE_INTERVAL_HOURS="${UPDATE_INTERVAL_HOURS:-24}"
RETRY_MINUTES="${RETRY_MINUTES:-60}"
RUN_ONCE="${RUN_ONCE:-0}"

update() {
  mkdir -p "$DEST" || return 1
  cd "$DEST" || return 1

  # CC BY-SA: the notice travels with the data. Restored unconditionally, not
  # only on the download path — otherwise deleting it (or a crash between the
  # two renames below) leaves the volume permanently without the notice while
  # we cheerfully report "up to date".
  [ -s ATTRIBUTION.txt ] || cp /opt/ipgeo/ATTRIBUTION.txt ATTRIBUTION.txt || return 1

  if ! curl -fsSL "$BASE/MANIFEST.json" -o MANIFEST.json.new; then
    echo "[ipgeo-updater] MANIFEST fetch failed (no release published yet, or network issue)" >&2
    rm -f MANIFEST.json.new
    return 1
  fi

  # "Up to date" requires the database to actually be present, not just a
  # matching manifest — otherwise a deleted DB is reported as healthy forever
  # and never re-downloaded. Presence check only: re-hashing ~200 MB on every
  # check would cost far more than the rare repair it would catch.
  if [ -f MANIFEST.json ] && cmp -s MANIFEST.json MANIFEST.json.new \
     && [ -s ipgeo-community.mmdb ]; then
    rm MANIFEST.json.new
    echo "[ipgeo-updater] up to date ($(jq -r .version MANIFEST.json))"
    return 0
  fi

  if ! curl -fsSL "$BASE/ipgeo-community.mmdb" -o ipgeo-community.mmdb.new; then
    echo "[ipgeo-updater] MMDB download failed" >&2
    rm -f ipgeo-community.mmdb.new MANIFEST.json.new
    return 1
  fi

  WANT=$(jq -r '.files["ipgeo-community.mmdb"].sha256' MANIFEST.json.new)
  GOT=$(sha256sum ipgeo-community.mmdb.new | cut -d' ' -f1)
  if [ "$WANT" != "$GOT" ]; then
    echo "[ipgeo-updater] checksum mismatch (want $WANT got $GOT) — keeping current DB" >&2
    rm -f ipgeo-community.mmdb.new MANIFEST.json.new
    return 1
  fi

  # Same directory ⇒ same filesystem ⇒ atomic rename; readers never see a torn file.
  # Each step is checked explicitly: `set -e` does NOT apply inside this function
  # (it is called as `if update`, which disables it for the whole body), so an
  # unchecked failure would fall through to the success echo below and report a
  # broken install as a good one. MMDB first — if it fails the old manifest is
  # left in place, so the next pass retries instead of trusting a new manifest.
  mv -f ipgeo-community.mmdb.new ipgeo-community.mmdb || return 1
  mv -f MANIFEST.json.new MANIFEST.json || return 1
  # CC BY-SA: the attribution notice travels with the data volume. Bare name,
  # not "$DEST/..." — we are already cd'd into $DEST, so prefixing it breaks a
  # relative DEST override (DEST=data would target data/data/ATTRIBUTION.txt).
  cp /opt/ipgeo/ATTRIBUTION.txt ATTRIBUTION.txt || return 1
  echo "[ipgeo-updater] updated to $(jq -r .version MANIFEST.json)"
}

echo "[ipgeo-updater] ipgeo Community Edition sidecar — keyless, no account; data updates weekly (Mondays)."
while :; do
  if update; then
    [ "$RUN_ONCE" = "1" ] && exit 0
    sleep $((UPDATE_INTERVAL_HOURS * 3600))
  else
    [ "$RUN_ONCE" = "1" ] && exit 1
    echo "[ipgeo-updater] retrying in ${RETRY_MINUTES}m"
    sleep $((RETRY_MINUTES * 60))
  fi
done
