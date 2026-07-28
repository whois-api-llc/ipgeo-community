# ipgeo Community Edition

A **free, no-signup** IP geolocation database (MMDB + CSV). What makes it different from other free
databases: it bundles city geolocation **with the VPN provider's name** behind an IP, plus a
datacenter flag and an infrastructure **`ip_type`** classification.

|  | GeoLite2 | DB-IP Lite | IP2Location LITE | X4BNet lists_vpn | **ipgeo Community** |
|---|:--:|:--:|:--:|:--:|:--:|
| City + ASN geolocation | ✔ | ✔ | ✔ | ✘ | **✔** |
| VPN flags | ✘ (paid) | ✘ | ✘ ¹ | ✔ | **✔** |
| VPN **provider names** | ✘ | ✘ | ✘ ¹ | ✘ ² | **✔ (where known)** |
| Infrastructure `ip_type` | ✘ | ✘ | partial ³ | partial ⁴ | **✔** |
| No account required | ✘ | ✔ | ✘ | ✔ | **✔** |
| License | EULA | CC BY 4.0 | Terms of Use ⁵ | MIT ⁶ | CC BY-SA 4.0 |

Every cell was re-checked against the vendor's own pages on **2026-07-28**; the footnotes quote them
so you can verify rather than take our word for it.

¹ IP2Location LITE's geolocation files carry no VPN or proxy field. Their free *proxy* database,
IP2Proxy LITE, is a separate download, and IP2Location states it "*is limited to public proxy (PUB)
IP addresses*", directing users to the commercial edition "*for IP addresses of VPN, web proxies,
Tor exits, data centers (DCH) and search engine robots (SES)*" — [PX11 LITE product
page](https://lite.ip2location.com/database/px11-ip-proxytype-country-region-city-isp-domain-usagetype-asn-lastseen-threat-residential-provider),
2,664,950 IPv4 rows. That schema does define a `provider` column ("*Name of VPN provider if
available*"); we have not downloaded the file to see whether it is populated, since that needs an
account.

² X4BNet's *published* lists are unlabelled CIDRs, so the distributed data carries no provider
names — but the same repository does publish provider attribution in its **input** files
(`input/vpn/ASN.txt` maps ASNs to named providers; `input/vpn/ips/` holds per-provider files).

³ IP2Proxy LITE carries a 12-value usage-type classification —
`(COM)(ORG)(GOV)(MIL)(EDU)(LIB)(CDN)(ISP)(MOB)(DCH)(SES)(RSV)` — but only across its ~2.66M
open-proxy records; the IP2Location LITE geolocation files themselves carry no such field.

⁴ X4BNet ships a separate datacenter list (`output/datacenter/ipv4.txt` — 42,552 CIDRs on
2026-07-28); it does not classify CDN, mobile carrier, satellite, education or government.

⁵ IP2Location applies no Creative Commons licence to IP2Location LITE; it ships under the licensor's
own [Terms of Use](https://lite.ip2location.com/data-license), which require attribution.

⁶ MIT, granted in the repository README's prose — there is no `LICENSE` file in
[X4BNet/lists_vpn](https://github.com/X4BNet/lists_vpn) and GitHub reports no licence for it.

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
95.3% · `asn` 80.6% · `as_org` 80.5% · `ip_type` 9.9% · `is_datacenter` 8.5% ·
**`postal_code` 0.9%** · `is_vpn` 0.03% · `is_proxy` 0% · `country_name` 0%.

`timezone` is **not always an IANA name**: 45.5% of records carry one (`America/New_York`) and
54.3% carry a bare UTC offset (`+10:00`). Test for `/` before handing the value to a tz library.

**VPN detection belongs to `community-vpn-list.csv`, not to the MMDB's `is_vpn`.** The list is the
authoritative VPN surface — 11,922 ranges (all IPv4; the list carries no IPv6 rows), and it is the
only place **provider names** exist. The MMDB flag is a narrower ASN-level subset: as of the
`2026-07-27` release it is set on 4,068 of those 11,922 ranges (34.1%), so reading `is_vpn` alone
under-detects and can never give you a provider name.

Full reference: [SCHEMA.md](SCHEMA.md).

## Quick start (Python)

Two files, two questions. Use the **MMDB** for *where is this IP*, and the **VPN list** for
*is this a VPN, and whose* — the MMDB's `is_vpn` is a narrower subset and never carries a provider
name, so a VPN check that reads only the MMDB will miss most of the list.

```python
import csv, gzip, ipaddress, maxminddb

# Geolocation → the MMDB.
reader = maxminddb.open_database("ipgeo-community.mmdb")
rec = reader.get("2.56.190.1")       # use .get() — this is not a typed geoip2 City database
print(rec["country_code"], rec.get("city"), rec.get("is_vpn"))

# VPN + provider name → community-vpn-list.csv (11,922 IPv4 ranges; no IPv6 rows).
with gzip.open("community-vpn-list.csv.gz", "rt", newline="") as f:
    vpn_ranges = [(ipaddress.ip_network(r["network"]), r["provider"], r["basis"])
                  for r in csv.DictReader(f)]

def vpn_lookup(ip):
    addr = ipaddress.ip_address(ip)
    return [(str(net), prov or "?", basis) for net, prov, basis in vpn_ranges if addr in net]

print(vpn_lookup("2.56.190.1"))
print(vpn_lookup("2606:4700:4700::1111"))
```

Actual output against the `2026-07-27` release:

```
US Dallas None
[('2.56.190.0/24', 'nordvpn', 'cluster')]
[]
```

That first line is the whole point: the MMDB geolocates `2.56.190.1` to Dallas and reports **no**
`is_vpn`, while the list names it as NordVPN. Querying an IPv6 address is safe — it simply matches
nothing, since the list is IPv4-only.

The MMDB works with any maxminddb reader (Python `maxminddb`, Go `oschwald/maxminddb-golang`,
Node `maxmind`) via the generic `.get()` — same file format as GeoLite2, with our own documented
fields. The linear scan above is fine for 11,922 ranges; for high-volume lookups load them into a
prefix trie instead.

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
trademarks of Hexasoft Development Sdn Bhd; DB-IP is a trademark of its operator; X4BNet/lists_vpn
and IPtoASN are the marks of their respective owners. This project is independent of, and not
affiliated with or endorsed by, any of them.*
