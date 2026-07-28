# Support

ipgeo Community Edition is a free, weekly-updated database maintained on a
**best-effort basis. There is no SLA** — no guaranteed response or fix time.
Issues are triaged roughly weekly, around the Monday release.

**Where to get help:** [GitHub issues](../../issues/new/choose) — pick the
bug, data-correction, or question template. There is no email support for the
free edition. Before filing, check the [README](README.md),
[SCHEMA.md](SCHEMA.md), and the FAQ below, and make sure you're on the
[latest weekly release](../../releases/latest).

## "My IP is located wrong"

IP geolocation is estimation, not measurement of you:

- **Country** is generally reliable; **city and region are approximate by
  nature** — data is per network prefix, and networks move and get
  reassigned.
- **Coordinates are the center of an estimated area** (often a city). They
  are never a street address, and can't identify a household or person.
- Data refreshes **weekly on Mondays** — first check whether the latest
  release still has the problem.

Still wrong? File a **Data correction** issue with the IP/CIDR, the field
that's wrong, what you expected, and evidence if you have it. The strongest
evidence is authoritative: an RIR registration, an operator-published
[RFC 8805 geofeed](https://www.rfc-editor.org/rfc/rfc8805) (if you operate
the network, publishing a geofeed is the most durable fix — the pipeline
ingests them), or official provider documentation.

**Corrections ship in a future weekly release** — accepted fixes appear in an
upcoming Monday build, never as a hotfix to an existing release.

### About the VPN / datacenter flags

`is_vpn`, `is_proxy`, `is_datacenter`, `ip_type`, and the VPN list are
**ASN/provider-level classifications by design** in the free edition. A
single address inside a provider's flagged range can't be individually
unflagged at this granularity — corrections apply at the range/provider
level (wrong provider name, a range that isn't the provider's anymore, a
mis-typed `ip_type`). Those corrections are welcome via the same template.

## Commercial / production needs

Per-IP precision, daily updates, confidence scores, and supported SLAs are
the commercial tier — [WhoisXML API IP Geolocation](https://ip-geolocation.whoisxmlapi.com/?utm_source=ipgeo-community&utm_medium=docs&utm_campaign=community-launch&utm_content=support).
Sales and licensing questions belong there, not in the issue tracker.

## Security

For anything security-sensitive about the release pipeline or artifacts, use
GitHub's private vulnerability reporting on this repo instead of a public
issue.

---

## FAQ

**How often is the database updated?**
Weekly, on Mondays. There is no fresher free feed — if you need daily
updates, that's the commercial tier.

**Can I use this commercially / redistribute it?**
Yes. The license is **CC BY-SA 4.0**: keep attribution (`ATTRIBUTION.txt`,
`VPN-ATTRIBUTION.txt`) and share derivative databases under compatible
terms.

**Why does `geoip2` / `GeoIP2-City` reader code fail on this file?**
The MMDB has database type `ipgeo` with a **flat** record schema. Typed
GeoLite2 wrappers validate the type string and nested layout and will error.
Use your language's generic maxminddb reader and `.get()` — see the README
quick start and [SCHEMA.md](SCHEMA.md).

**Why is a field missing for some IPs?**
Fields are **absent when unknown** rather than filled with guesses. Code
defensively (`rec.get("city")`, not `rec["city"]`).

**A cloud/datacenter IP I use is flagged `is_datacenter` — is that a bug?**
Usually not: the flag describes the *infrastructure* (hosted address space),
not your application. An IP can be a legitimate business server and still be
datacenter space. `ip_type` adds the finer class (`datacenter`, `cdn`,
`mobile_carrier`, `satellite`, `education`, `government`).

**How is the free VPN list different from the paid data?**
The free list is aggregated at ASN/provider level with provider names where
known. The commercial products add per-IP precision, daily cadence, and
confidence scoring. The free tier is honest about that boundary — it's why
it exists.

**Which file should I use?**
`ipgeo-community.mmdb` for lookups in applications; the CSVs for SQL or
dataframe analysis; `community-vpn-list.csv.gz` if you only want the VPN
ranges. `MANIFEST.json` carries the checksums for all of them.

**Where do I report a wrong provider name in the VPN list?**
Data correction issue, range-level, with whatever documentation you have —
provider attributions are curated and reviewed manually.
