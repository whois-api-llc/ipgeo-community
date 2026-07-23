# ipgeo Community Edition

A **free, no-signup** IP geolocation database (MMDB + CSV) with something no
other free database bundles: **VPN / proxy / datacenter flags** and an
**`ip_type`** infrastructure classification, plus a **provider-named VPN list**.

| | GeoLite2 | DB-IP Lite | IP2Location LITE | **ipgeo Community** |
|---|---|---|---|---|
| City + ASN | ✔ | ✔ | ✔ | ✔ |
| VPN / proxy flags | ✘ (paid) | ✘ | ✘ (open-proxy only) | **✔** |
| Infra `ip_type` | ✘ | ✘ | ✘ | **✔** |
| Provider-named VPN list | ✘ | ✘ | ✘ | **✔** |
| No account | ✘ | ✔ | ✘ | **✔** |

## Download

Grab the latest [Release](../../releases/latest):
- `ipgeo-community.mmdb` — MaxMind DB format (any maxminddb reader)
- `ipgeo-community.csv.gz` — same records as CSV
- `community-vpn-list.csv.gz` — ASN/provider VPN ranges (`network,provider,basis`)
- `MANIFEST.json` — version, checksums, row counts

## Fields

`country`, `region`, `city`, `latitude`, `longitude`, `timezone`, `asn`,
`as_org`, `is_vpn`, `is_proxy`, `is_datacenter`, `ip_type`
(datacenter / cdn / mobile_carrier / satellite / education / government).

## License

CC BY-SA 4.0 — see [LICENSE](LICENSE) and [ATTRIBUTION.txt](ATTRIBUTION.txt).
Updated weekly. Need per-IP VPN precision, daily updates, or confidence
scores? Those are in the commercial WhoisXML / Panavision products.
