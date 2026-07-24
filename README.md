# ipgeo Community Edition

A **free, no-signup** IP geolocation database (MMDB + CSV). What makes it different from other free
databases: it's the only free **download** that bundles city geolocation **with the VPN provider's
name** behind an IP, plus proxy / datacenter flags and an infrastructure **`ip_type`** classification.

|  | GeoLite2 | DB-IP Lite | IP2Location LITE | X4BNet lists_vpn | **ipgeo Community** |
|---|:--:|:--:|:--:|:--:|:--:|
| City + ASN geolocation | ✔ | ✔ | ✔ | ✘ | **✔** |
| VPN flags | ✘ (paid) | ✘ | ✘ ¹ | ✔ | **✔** |
| VPN **provider names** | ✘ | ✘ | ✘ | ✘ | **✔ (where known)** |
| Infrastructure `ip_type` | ✘ | ✘ | ✘ | ✘ | **✔** |
| No account required | ✘ | ✔ | ✘ | ✔ | **✔** |
| License | EULA | CC BY 4.0 | CC BY-SA 4.0 | MIT | CC BY-SA 4.0 |

¹ IP2Location's free *proxy* list (IP2Proxy LITE) is open-proxy only and ships **zero VPN records**.

## Download

Grab the latest [Release](../../releases/latest):
- `ipgeo-community.mmdb` — MaxMind DB format; read it with **any maxminddb reader's generic `.get()` API**
- `ipgeo-community.csv.gz` — the same records as CSV
- `community-vpn-list.csv.gz` — ASN/provider-level VPN ranges (`network,provider,basis`)
- `SCHEMA.md` — field reference
- `MANIFEST.json` — version, checksums, row counts

## Fields

`country_code`, `country_name`, `region`, `city`, `postal_code`, `latitude`, `longitude`,
`timezone`, `asn`, `as_org`, `is_vpn`, `is_proxy`, `is_datacenter`, `ip_type`
(`datacenter` / `cdn` / `mobile_carrier` / `satellite` / `education` / `government`).
A field is **absent** when unknown. Full reference: [SCHEMA.md](SCHEMA.md).

## Quick start (Python)

```python
import maxminddb
reader = maxminddb.open_database("ipgeo-community.mmdb")
rec = reader.get("1.1.1.1")          # use .get() — this is not a typed geoip2 City database
print(rec["country_code"], rec.get("is_vpn"), rec.get("ip_type"))
```

Works with any maxminddb reader (Python `maxminddb`, Go `oschwald/maxminddb-golang`,
Node `maxmind`) via the generic `.get()` — same file format as GeoLite2, with our own documented fields.

## License

**CC BY-SA 4.0** — see [LICENSE](LICENSE) and [ATTRIBUTION.txt](ATTRIBUTION.txt). You must keep the
attribution notices and share derivatives alike. Updated weekly.

## Free vs. commercial

The free edition uses **ASN / network-block** granularity, native flags, and a weekly cadence. Need
**per-IP (/32) precision, daily updates, or confidence scores**? Those are the commercial
[WhoisXML / Panavision](https://www.whoisxmlapi.com/?utm_source=ipgeo-community&utm_medium=readme&utm_campaign=community-launch)
products.

---
*Trademarks: MaxMind and GeoLite2 are trademarks of MaxMind, Inc.; IP2Location and IP2Proxy are
trademarks of Hexasoft Online Sdn Bhd; DB-IP is a trademark of its operator; X4BNet/lists_vpn and
IPtoASN are the marks of their respective owners. This project is independent of, and not affiliated
with or endorsed by, any of them.*
