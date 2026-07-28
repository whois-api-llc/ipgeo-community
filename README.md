# ipgeo Community Edition

A **free, no-signup** IP geolocation database (MMDB + CSV). What makes it different from other free
databases: it's the only free **download** that bundles city geolocation **with the VPN provider's
name** behind an IP, plus a datacenter flag and an infrastructure **`ip_type`** classification.

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
A field is **absent** when unknown — coverage varies by field, so check before you build on one.
Two columns are part of the schema but **reserved — they carry no data in the current release**:

- **`is_proxy` — reserved, never set.** The free edition derives its flags from ASN
  classification and its proxy-ASN list is empty, so this flag is not populated in any record.
- **`country_name` — reserved, not populated.** Derive it from `country_code`.

Per-field coverage, measured over all 27,344,365 records of the `2026-07-27` release:
`country_code` 99.9% · `timezone` 99.8% · `city` 97.5% · `region` 97.1% · `latitude`/`longitude`
95.3% · `asn`/`as_org` 80.6% · `ip_type` 9.9% · `is_datacenter` 8.5% · **`postal_code` 0.9%** ·
`is_vpn` 0.03% · `is_proxy` 0% · `country_name` 0%.

`timezone` is **not always an IANA name**: 45.5% of records carry one (`America/New_York`) and
54.3% carry a bare UTC offset (`+10:00`). Test for `/` before handing the value to a tz library.

**VPN detection belongs to `community-vpn-list.csv`, not to the MMDB's `is_vpn`.** The list is the
authoritative VPN surface — 11,922 ranges, and it is the only place **provider names** exist. The
MMDB flag is a narrower ASN-level subset: it is set on 4,068 of those 11,922 IPv4 ranges (34.1%),
so reading `is_vpn` alone under-detects and can never give you a provider name.

Full reference: [SCHEMA.md](SCHEMA.md).

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
[WhoisXML API IP Geolocation](https://ip-geolocation.whoisxmlapi.com/?utm_source=ipgeo-community&utm_medium=readme&utm_campaign=community-launch)
products.

---
*Trademarks: MaxMind and GeoLite2 are trademarks of MaxMind, Inc.; IP2Location and IP2Proxy are
trademarks of Hexasoft Online Sdn Bhd; DB-IP is a trademark of its operator; X4BNet/lists_vpn and
IPtoASN are the marks of their respective owners. This project is independent of, and not affiliated
with or endorsed by, any of them.*
