#!/usr/bin/env python3
# VENDORED from topcoder1/ipgeo_core `scripts/gen_release_notes.py` (PR #179),
# which holds the source of truth and the test suite. Re-vendor from there
# rather than editing this copy — local-only edits get silently overwritten.
"""Generate weekly release notes for the ipgeo Community Edition from MANIFEST.json.

Renders markdown to stdout from artifact-level facts only: record counts,
VPN-list rows, file sizes + checksums, and (optionally) week-over-week deltas
vs the previous MANIFEST and the provider-named share of the VPN list computed
from the shipped community-vpn-list CSV itself.

Guardrail (GTM §1.5): the render is public marketing surface. Enforcement is
STRUCTURAL, not a denylist — every manifest value that reaches the output must
pass a strict allowlist (validate_manifest), and the script fails closed
(exit 1, nothing rendered) on any violation. Percentages are computed fresh
per build (the own-metrics freshness rule) and tagged to this release.

Usage:
  python3 scripts/gen_release_notes.py MANIFEST.json \
      [--prev previous/MANIFEST.json] [--vpn-list community-vpn-list.csv.gz] \
      [--commercial-url https://ip-geolocation.whoisxmlapi.com/]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import ipaddress
import json
import pathlib
import re
import sys

DEFAULT_COMMERCIAL_URL = "https://ip-geolocation.whoisxmlapi.com/"

# Schema fields that exist in the artifact but carry no value on any record, so
# the notes must never advertise them as signal. `is_proxy` is empty BY
# CONSTRUCTION: the community build recomputes the flag from
# pipeline.sources.vpn_detect.detect_asn, whose PROXY_ASNS is an empty
# frozenset, so it can only ever come out false (0 / 27,344,365 rows in
# community-2026-07-27; same scan found country_name at 0 too). Names here are
# used for MEMBERSHIP against the manifest's column list only — what the render
# prints is this module's own literals, never manifest-supplied text.
RESERVED_FIELDS = ("country_name", "is_proxy")

# Populated flag/classification fields, in the order the bullet names them.
HEADLINE_FIELDS = ("is_vpn", "is_datacenter", "ip_type")

CTA = (
    "Need per-IP VPN precision, daily updates, or confidence scores? "
    "[Commercial tier]({url}?utm_source=ipgeo-community"
    "&utm_medium=release-notes&utm_campaign=community-launch&utm_content={version})."
)

# Allowlists for every manifest-sourced string that reaches the public render.
_VERSION_RE = re.compile(r"^[0-9][0-9A-Za-z._-]{0,63}$")
_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_manifest(manifest: dict) -> dict:
    """Fail-closed normalization: only allowlisted values may reach the render.

    Raises ValueError on anything unexpected — a weird version string, file
    name, or checksum means the notes are NOT generated (never "rendered
    anyway"), so no upstream content can be echoed onto the public surface.
    """
    if not isinstance(manifest, dict):
        raise ValueError("manifest is not a JSON object")
    version = str(manifest.get("version", ""))
    if not _VERSION_RE.match(version):
        raise ValueError(f"manifest version fails the allowlist: {version!r}")
    columns = [str(c) for c in (manifest.get("columns") or [])]
    out = {
        "version": version,
        "records": int(manifest.get("records") or 0),
        "vpn_list_rows": int(manifest.get("vpn_list_rows") or 0),
        "n_columns": len(columns),
        # Membership set only — column names are never echoed into the render,
        # so they need no allowlist and an unusual name cannot break a release.
        "column_names": frozenset(columns),
        "files": {},
    }
    for name, meta in (manifest.get("files") or {}).items():
        if not _FILENAME_RE.match(str(name)):
            raise ValueError(f"file name fails the allowlist: {name!r}")
        sha = str((meta or {}).get("sha256", ""))
        if not _SHA256_RE.match(sha):
            raise ValueError(f"sha256 for {name} fails the allowlist: {sha!r}")
        out["files"][str(name)] = {"bytes": int((meta or {}).get("bytes") or 0), "sha256": sha}
    return out


def _human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def _delta(cur: int, prev: int | None) -> str:
    if prev is None:
        return "first release"
    d = cur - prev
    return f"{'+' if d >= 0 else ''}{d:,} vs last week"


def _union_addresses(nets: list[ipaddress.IPv4Network]) -> int:
    """Size of the UNION of `nets` in addresses — each address counted once.

    `collapse_addresses` drops networks subsumed by a larger one and merges
    adjacent siblings; neither changes the union's size, so summing the
    collapsed result is an exact de-duplicated count.
    """
    return sum(n.num_addresses for n in ipaddress.collapse_addresses(nets))


def vpn_named_share(path: pathlib.Path) -> tuple[float, int] | None:
    """(provider-named % of listed IPv4 space, total rows) from network,provider,basis CSV.

    Both sides are de-overlapped before their address counts are summed. The
    list carries the same address space under more than one `basis` (`asn`,
    `x4bnet`, `cluster`), so a per-row sum double-counts every overlapping
    prefix. That inflates the DENOMINATOR far more than the numerator (named
    ranges do not overlap each other), which understates the published share.
    Counting each side as a union is the honest figure.
    """
    opener = gzip.open if path.suffix == ".gz" else open
    named_nets: list[ipaddress.IPv4Network] = []
    all_nets: list[ipaddress.IPv4Network] = []
    rows = 0
    try:
        with opener(path, "rt", newline="") as f:
            for row in csv.DictReader(f):
                rows += 1
                try:
                    net = ipaddress.ip_network(row["network"], strict=False)
                except (KeyError, ValueError):
                    continue
                if net.version != 4:
                    continue
                all_nets.append(net)
                if (row.get("provider") or "").strip():
                    named_nets.append(net)
    except OSError as e:
        print(f"note: cannot read vpn list ({e}) — omitting provider-share line", file=sys.stderr)
        return None
    total = _union_addresses(all_nets)
    if total == 0:
        if rows:
            # Rows existed but none parsed — schema drift, not an empty list. Say so.
            print(
                f"note: vpn list has {rows} rows but no parseable IPv4 'network' column "
                "— schema drift? omitting provider-share line",
                file=sys.stderr,
            )
        return None
    return (100.0 * _union_addresses(named_nets) / total, rows)


def render_notes(
    manifest: dict,
    prev: dict | None = None,
    vpn_stats: tuple[float, int] | None = None,
    commercial_url: str = DEFAULT_COMMERCIAL_URL,
) -> str:
    m = validate_manifest(manifest)
    p = validate_manifest(prev) if prev else None
    version = m["version"]

    lines = [
        f"# ipgeo Community Edition — {version}",
        "",
        "Free IP geolocation database with VPN and datacenter flags, a",
        "provider-named VPN list, and `ip_type` infrastructure classification.",
        "**CC BY-SA 4.0** · updated **weekly on Mondays** · no signup.",
        "",
        "## This release",
        "",
        f"- **{m['records']:,}** prefix records ({_delta(m['records'], p['records'] if p else None)})",
        f"- **{m['vpn_list_rows']:,}** VPN-list ranges "
        f"({_delta(m['vpn_list_rows'], p['vpn_list_rows'] if p else None)})",
    ]
    if vpn_stats:
        pct, _ = vpn_stats
        lines.append(f"- Provider names on **{pct:.1f}%** of the listed IPv4 space (as of release {version})")
    if m["n_columns"]:
        populated = " / ".join(f"`{f}`" for f in HEADLINE_FIELDS)
        lines.append(f"- {m['n_columns']} fields incl. {populated}")
        reserved = [f for f in RESERVED_FIELDS if f in m["column_names"]]
        if reserved:
            names = " and ".join(f"`{f}`" for f in reserved)
            lines.append(
                f"- {names} are part of the schema but are RESERVED — not populated in this "
                "release, so treat them as absent rather than as a negative signal"
                if len(reserved) > 1
                else f"- {names} is part of the schema but is RESERVED — not populated in this "
                "release, so treat it as absent rather than as a negative signal"
            )

    if m["files"]:
        lines += ["", "## Files", "", "| File | Size | SHA-256 |", "| --- | --- | --- |"]
        for name, meta in m["files"].items():
            lines.append(f"| `{name}` | {_human_bytes(meta['bytes'])} | `{meta['sha256']}` |")
        lines += [
            "",
            "Verify downloads against `MANIFEST.json` (the checksum contract — see the",
            "keep-updated guide). CSV checksums cover the decompressed content.",
        ]

    lines += [
        "",
        "## Attribution",
        "",
        "Includes DB-IP Lite (CC BY 4.0), X4BNet lists_vpn (MIT), and IPtoASN",
        "([PDDL v1.0](https://opendatacommons.org/licenses/pddl/1.0/)) data.",
        "",
        "Keep `ATTRIBUTION.txt` and `VPN-ATTRIBUTION.txt` alongside redistributed",
        "copies.",
        "",
        "---",
        "",
        CTA.format(url=commercial_url, version=version),
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("manifest", type=pathlib.Path)
    ap.add_argument("--prev", type=pathlib.Path, help="previous release's MANIFEST.json")
    ap.add_argument("--vpn-list", type=pathlib.Path, help="community-vpn-list.csv[.gz]")
    ap.add_argument(
        "--commercial-url",
        default=DEFAULT_COMMERCIAL_URL,
        help="base URL for the upgrade CTA (default: %(default)s)",
    )
    args = ap.parse_args(argv)

    try:
        manifest = json.loads(args.manifest.read_text())
        prev = json.loads(args.prev.read_text()) if args.prev else None
        vpn_stats = vpn_named_share(args.vpn_list) if args.vpn_list else None
        notes = render_notes(manifest, prev, vpn_stats, args.commercial_url)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"FATAL: refusing to render notes: {e}", file=sys.stderr)
        return 1

    print(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
