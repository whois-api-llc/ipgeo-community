# ipgeo Community Edition — field reference

Read the MMDB with any maxminddb reader's generic `.get(ip)`. This is
`DatabaseType: "ipgeo"` with a FLAT record schema — it is NOT a typed geoip2
City database, so use `.get()`, not `.city()`. A field is ABSENT from a record
when unknown.

| Field           | Type    | Populated ¹ | Notes                                       |
| --------------- | ------- | ----------: | ------------------------------------------- |
| `country_code`  | string  | 99.99%      | ISO 3166-1 alpha-2 (e.g. "US")              |
| `country_name`  | string  | 99.99%      | English country name, derived from `country_code` |
| `region`        | string  | 93.39%      | Region / state name                         |
| `city`          | string  | 94.73%      | City name                                   |
| `postal_code`   | string  | **1.10%**   | Postal / ZIP code where known — present on a small minority of records; do not build on it |
| `latitude`      | float64 | 88.60%      | WGS84                                       |
| `longitude`     | float64 | 88.60%      | WGS84                                       |
| `timezone`      | string  | 99.93%      | IANA tz name (e.g. "America/New_York") on every populated record of the `2026-11-02` release |
| `asn`           | uint32  | 92.44%      | Autonomous System Number                    |
| `as_org`        | string  | 92.44%      | AS organization / operator                  |
| `is_vpn`        | bool    | 0.05%       | true when the ASN is a known VPN network (native ASN). Narrower than `community-vpn-list.csv` — read that list for VPN detection and provider names |
| `is_proxy`      | bool    | **0%**      | **Reserved, not populated in the current release** — the free edition's proxy-ASN list is empty, so the flag is never set on any record |
| `is_datacenter` | bool    | 4.00%       | true when the ASN is datacenter / hosting   |
| `ip_type`       | string  | 6.40%       | datacenter / cdn / mobile_carrier / satellite / education / government |
| `sanctioned_region` | bool | 0.002% ² | true for networks placed in Crimea or Sevastopol by region or coordinates, and for networks with no region or coordinates of their own whose nearest enclosing network with either is one of them; all are coded `country_code` UA; absent elsewhere. Any other network located only by its city name, or not at all, carries no flag, so its absence does not prove a network is elsewhere. It does not mark the occupied parts of the Donetsk, Luhansk, Zaporizhzhia or Kherson oblasts |

¹ Share of the 16,552,600 records (rows of the CSV) in the `2026-11-02` release carrying a
non-empty value for the field. The MMDB resolves overlapping rows into fewer records, so its
shares differ. Coverage moves between weekly releases; the row marked **reserved** is
structural, not a coverage dip — it stays in the schema and in `MANIFEST.json`'s `columns`
so readers keep a stable column order, but nothing populates it today.

² `sanctioned_region` is new in the `2026-11-02` release: 344 of the 16,552,600 records in its CSV
carry it.

The boolean flags are **true-only**: they are present exactly when set, and absent otherwise —
no record carries an explicit `false`. Read them with `rec.get("is_datacenter")` and treat a
missing key as "not flagged", never as "unknown vs. false".

## community-vpn-list.csv — the VPN surface

Columns `network,provider,basis` — `basis` is `asn`, `x4bnet`, or `cluster`;
`provider` is the VPN brand where known. Rows with `basis=x4bnet` are used under
the MIT license (see VPN-ATTRIBUTION.txt, shipped with the release).

**This list, not the MMDB's `is_vpn`, is the VPN surface.** The MMDB flag is an ASN-level
signal and is deliberately narrower: as of the `2026-11-02` release, of the list's 11,786 IPv4
ranges (it carries no IPv6 rows), 4,063 (34.5%) have `is_vpn` set on their MMDB record (the one
for each range's first address), and of the 2,673 provider-named ranges, 1,314 (49.2%) do. **Provider names are not in the MMDB at all.**
For VPN detection or provider attribution, match against this list; use the MMDB flag only as a
coarse hint. These shares are re-measured per release — check the current one rather than
assuming last week's.

The same range can appear under more than one `basis`, so the rows overlap — de-overlap them
(e.g. `ipaddress.collapse_addresses`) before summing address counts, or you will double-count.

## Not included (commercial WhoisXML API products only)

Per-IP (/32) precision and daily cadence.
