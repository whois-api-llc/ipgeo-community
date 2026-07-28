# ipgeo Community Edition — field reference

Read the MMDB with any maxminddb reader's generic `.get(ip)`. This is
`DatabaseType: "ipgeo"` with a FLAT record schema — it is NOT a typed geoip2
City database, so use `.get()`, not `.city()`. A field is ABSENT from a record
when unknown.

| Field           | Type    | Notes                                                    |
| --------------- | ------- | -------------------------------------------------------- |
| `country_code`  | string  | ISO 3166-1 alpha-2 (e.g. "US")                           |
| `country_name`  | string  | English country name — **not populated in the current release**; derive from `country_code` |
| `region`        | string  | Region / state name                                      |
| `city`          | string  | City name                                                |
| `postal_code`   | string  | Postal / ZIP code where known                            |
| `latitude`      | float64 | WGS84                                                    |
| `longitude`     | float64 | WGS84                                                    |
| `timezone`      | string  | IANA tz name (e.g. "America/New_York") **or** UTC offset (e.g. "+10:00") — test for "/" before treating it as an IANA zone |
| `asn`           | uint32  | Autonomous System Number                                 |
| `as_org`        | string  | AS organization / operator                               |
| `is_vpn`        | bool    | true when the ASN is a known VPN network (native ASN)    |
| `is_proxy`      | bool    | true when the ASN is a known proxy network               |
| `is_datacenter` | bool    | true when the ASN is datacenter / hosting                |
| `ip_type`       | string  | datacenter / cdn / mobile_carrier / satellite / education / government |

## community-vpn-list.csv

Columns `network,provider,basis` — `basis` is `asn`, `x4bnet`, or `cluster`;
`provider` is the VPN brand where known. Rows with `basis=x4bnet` are used under
the MIT license (see VPN-ATTRIBUTION.txt, shipped with the release).

## Not included (commercial WhoisXML API products only)

Per-IP (/32) precision, confidence scores, `observed_*` fields, suspect classes,
and daily cadence.
