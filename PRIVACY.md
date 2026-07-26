# Privacy

Two separate things live under this project, and they have different privacy answers.
This page states what each one actually does.

For the company-level relationship — support requests, sales enquiries, the commercial
tier — see the
[WhoisXML API privacy policy](https://main.whoisxmlapi.com/privacy-policy). That policy
describes the company's websites and commercial services. **It does not describe the
hosted demo below**, which collects considerably less.

## 1. The database

The published database maps **network blocks** to location and infrastructure attributes.
Every row is a CIDR prefix — `1.2.3.0/24` — not an individual address, and the shipped
fields are:

`network`, `country_code`, `country_name`, `region`, `city`, `postal_code`, `latitude`,
`longitude`, `timezone`, `asn`, `as_org`, `is_vpn`, `is_proxy`, `is_datacenter`, `ip_type`

There are **no names, no subscriber records, no per-person data, and no per-IP records** of
any kind. `as_org` is the network operator — a company, not a person.

Two things this means in practice:

- **Coordinates are not an address.** They are the approximate centre of a network block,
  which can span a city or a country. They do not identify a household, a building, or a
  person, and must not be used as if they did.
- **The flags describe a network, not a user.** `is_vpn` on a block means the block is
  operated as VPN infrastructure. It is not a judgement about anyone using an address in
  that range.

Per-IP precision, daily updates, and confidence scores are deliberately **not** in this free
tier — see the README.

## 2. The hosted demo

The demo looks up an IP address against the database and shows the result. Its behaviour,
as implemented:

|                          |                                                                                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Access logs**          | None. Per-request logging is disabled in the application.                                                                                            |
| **Cookies**              | None set.                                                                                                                                            |
| **Analytics / trackers** | None.                                                                                                                                                |
| **Stored lookups**       | None. The address is used in memory to perform the lookup and is not written anywhere.                                                               |
| **Third-party requests** | None. The page loads no external scripts, fonts, or images.                                                                                          |
| **Your own IP**          | If you visit without specifying an address, the page looks up the address your request arrives from, so you see your own result. It is not retained. |

If you would rather not have your own address looked up at all, pass one explicitly —
`?ip=8.8.8.8` — and yours is never read.

The demo is **self-hostable** — the source is in [`demo/`](demo/) in this repository. Run your
own copy and nothing touches our infrastructure at all.

## Reporting a problem

If a record about your network is wrong, open a
[data correction issue](https://github.com/whois-api-llc/ipgeo-community/issues/new/choose).
The durable fix for an operator is to publish a
[geofeed](https://www.rfc-editor.org/rfc/rfc8805.html), which upstream sources pick up.

For anything concerning personal data, contact WhoisXML API through the channels in the
[privacy policy](https://main.whoisxmlapi.com/privacy-policy) above.
