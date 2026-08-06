#!/usr/bin/env python3
"""Refuse to ship a uniqueness claim about VPN provider names.

WHY THIS EXISTS
---------------
Until 2026-08-05 README.md said this was "the only free **download** that
bundles city geolocation **with the VPN provider's name** behind an IP", and a
footnote said IP2Proxy LITE "ships zero VPN records". Both were false, and the
footnote is the sharper error because it stated a measurable fact.

Measured on the free IP2Proxy LITE PX11 CSV (2,673,876 rows, downloaded
2026-08-05):

    provider populated                    25,963
    provider AND city_name                25,836
    of those, consumer VPN brands          8,100
      ExpressVPN 3,620 · UnitVpn 2,596 · Mysterium VPN 800 · VPNUnlockMe 658
      NordVPN 215 · ProtonVPN 172 · IPVanish 20 · Windscribe 19

This database carries 2,917 provider-named ranges. A free competitor names MORE
provider-attributed VPN ranges than we do, on the same row, while ours needs a
join across two shipped files.

The defence that made the claim look safe was a vendor's own prose: IP2Location
describes LITE as "limited to public proxy (PUB) IP addresses". That is
accurate -- every PX11 row is proxy_type=PUB -- but PUB-labelled ranges still
carry VPN provider names, because VPN exit nodes get catalogued as public
proxies. A vendor's description of their own free tier is not a measurement of
it, and reading one as the other is what put a false claim on the front page.

WHAT THIS DOES NOT DO
---------------------
It does not re-measure. That needs a 22MB download and an API token, so it
would make every PR depend on a third party being up. It pins the cheap half:
that nobody reinstates the superlative without redoing the measurement.

The logic lives here rather than inline in the workflow because logic written
as YAML is unreachable by tests -- run `--selftest` to see this checker prove
it can actually fail.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Files that pitch this database to a reader.
SURFACES = ("README.md",)

UNIQUENESS = re.compile(
    r"\b(only free (download|database)|uniquely among|no other free|first free"
    r"|zero VPN records|ships no VPN)\b",
    re.IGNORECASE,
)

# The claim only counts when it is ABOUT provider names. A uniqueness claim
# regarding something else is not this defect.
SUBJECT = re.compile(r"provider'?s? names?|provider attribution", re.IGNORECASE)

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
BLOCKQUOTE = re.compile(r"^\s*>.*$", re.MULTILINE)
FOOTNOTE = re.compile(r"^¹.*$", re.MULTILINE)


def prose(text: str) -> str:
    """Drop the places the retired claim is DOCUMENTED rather than MADE.

    Footnote 1 quotes the old wording in order to correct it. Without this the
    checker would forbid explaining its own reason for existing.
    """
    for pattern in (HTML_COMMENT, BLOCKQUOTE, FOOTNOTE):
        text = pattern.sub("", text)
    return text


def violations(text: str) -> list[str]:
    """Uniqueness claims made about provider names, with surrounding context."""
    body = prose(text)
    found = []
    for match in UNIQUENESS.finditer(body):
        window = body[max(0, match.start() - 300) : match.end() + 300]
        if SUBJECT.search(window):
            found.append(f"{match.group(0)!r} — ...{' '.join(window.split())[:180]}...")
    return found


def selftest() -> int:
    """Prove the checker can fail. A guard that only ever passes is not a guard.

    There is no pytest in this repo, so the checker carries its own proof.
    """
    must_catch = [
        "it's the only free download that bundles city with the VPN provider's name",
        "uniquely among free downloads — the VPN provider's name",
        "IP2Proxy LITE ships zero VPN records, so provider names are ours alone",
    ]
    must_allow = [
        "the only free download with a permissive licence",  # not about providers
        "we carry VPN provider names on 2,917 ranges",  # a count, not a superlative
        "<!-- was: the only free download with the VPN provider's name -->",
        "> Do not call this the only free download with VPN provider names.",
    ]
    failures = 0
    for sample in must_catch:
        if not violations(sample):
            print(f"SELFTEST FAIL — should have caught: {sample!r}", file=sys.stderr)
            failures += 1
    for sample in must_allow:
        if violations(sample):
            print(f"SELFTEST FAIL — false positive on: {sample!r}", file=sys.stderr)
            failures += 1
    if failures:
        return 1
    print(f"selftest ok — {len(must_catch)} caught, {len(must_allow)} allowed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="prove the checker can fail")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    # Run the selftest on every real invocation too, so a checker broken by a
    # careless edit fails loudly instead of passing everything.
    if selftest() != 0:
        return 1

    failed = False
    for name in SURFACES:
        path = REPO_ROOT / name
        if not path.exists():
            print(f"ERROR: {name} is missing — update SURFACES", file=sys.stderr)
            failed = True
            continue
        for hit in violations(path.read_text()):
            print(f"ERROR: {name} reinstates a uniqueness claim: {hit}", file=sys.stderr)
            failed = True

    if failed:
        print(
            "\nThis superlative was MEASURED FALSE on 2026-08-05: free IP2Proxy "
            "LITE PX11 carries `provider` alongside `city_name` on 25,836 ranges, "
            "8,100 of them consumer VPN brands, against our 2,917.\n"
            "If you believe it is true again, re-run the measurement first — and "
            "note that a vendor's description of their own tier is not one.\n"
            "See scripts/check_claims.py and ipgeo_core#246.",
            file=sys.stderr,
        )
        return 1

    print(f"ok — no unverified uniqueness claim in {', '.join(SURFACES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
