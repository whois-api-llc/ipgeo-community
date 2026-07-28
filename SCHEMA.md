# ipgeo Community Edition — field reference

Read the MMDB with any maxminddb reader's generic `.get(ip)`. This is
`DatabaseType: "ipgeo"` with a FLAT record schema — it is NOT a typed geoip2
City database, so use `.get()`, not `.city()`. A field is ABSENT from a record
when unknown.

| Field           | Type    | Populated ¹ | Notes                                       |
| --------------- | ------- | ----------: | ------------------------------------------- |
| `country_code`  | string  | 99.94%      | ISO 3166-1 alpha-2 (e.g. "US")              |
| `country_name`  | string  | **0%**      | English country name — **reserved, not populated in the current release**; derive it from `country_code` |
| `region`        | string  | 97.08%      | Region / state name                         |
| `city`          | string  | 97.48%      | City name                                   |
| `postal_code`   | string  | **0.93%**   | Postal / ZIP code where known — present on a small minority of records; do not build on it |
| `latitude`      | float64 | 95.31%      | WGS84                                       |
| `longitude`     | float64 | 95.31%      | WGS84                                       |
| `timezone`      | string  | 99.83%      | IANA tz name (e.g. "America/New_York") on 45.5% of records **or** a bare UTC offset (e.g. "+10:00") on 54.3% — test for "/" before treating it as an IANA zone |
| `asn`           | uint32  | 80.56%      | Autonomous System Number                    |
| `as_org`        | string  | 80.55%      | AS organization / operator                  |
| `is_vpn`        | bool    | 0.03%       | true when the ASN is a known VPN network (native ASN). Narrower than `community-vpn-list.csv` — read that list for VPN detection and provider names |
| `is_proxy`      | bool    | **0%**      | **Reserved, not populated in the current release** — the free edition's proxy-ASN list is empty, so the flag is never set on any record |
| `is_datacenter` | bool    | 8.49%       | true when the ASN is datacenter / hosting   |
| `ip_type`       | string  | 9.86%       | datacenter / cdn / mobile_carrier / satellite / education / government |

¹ Share of the 27,344,365 records in the `2026-07-27` release carrying a non-empty value for
the field. Coverage moves between weekly releases; the two rows marked **reserved** are
structural, not a coverage dip — they stay in the schema and in `MANIFEST.json`'s `columns`
so readers keep a stable column order, but nothing populates them today.

The boolean flags are **true-only**: they are present exactly when set, and absent otherwise —
no record carries an explicit `false`. Read them with `rec.get("is_datacenter")` and treat a
missing key as "not flagged", never as "unknown vs. false".

## community-vpn-list.csv — the VPN surface

Columns `network,provider,basis` — `basis` is `asn`, `x4bnet`, or `cluster`;
`provider` is the VPN brand where known. Rows with `basis=x4bnet` are used under
the MIT license (see VPN-ATTRIBUTION.txt, shipped with the release).

**This list, not the MMDB's `is_vpn`, is the VPN surface.** The MMDB flag is an ASN-level
signal and is deliberately narrower: of the list's 11,922 IPv4 ranges, 4,068 (34.1%) have
`is_vpn` set on their MMDB record, and of the 2,878 provider-named ranges, 1,465 (50.9%) do.
**Provider names are not in the MMDB at all.** For VPN detection or provider attribution,
match against this list; use the MMDB flag only as a coarse hint.

The same range can appear under more than one `basis`, so the rows overlap — de-overlap them
(e.g. `ipaddress.collapse_addresses`) before summing address counts, or you will double-count.

## Not included (commercial WhoisXML API products only)

Per-IP (/32) precision, confidence scores, `observed_*` fields, suspect classes,
and daily cadence.
