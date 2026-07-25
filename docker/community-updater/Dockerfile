FROM alpine:3.20

RUN apk add --no-cache curl jq ca-certificates tini

COPY ATTRIBUTION.txt /opt/ipgeo/ATTRIBUTION.txt
COPY update.sh /usr/local/bin/update.sh
RUN chmod +x /usr/local/bin/update.sh

VOLUME /data

LABEL org.opencontainers.image.title="ipgeo-community-updater" \
      org.opencontainers.image.description="Keyless weekly refresh sidecar for the free ipgeo Community Edition MMDB — checksum-verified, atomic swap, no account required. Database license: CC BY-SA 4.0." \
      org.opencontainers.image.source="https://github.com/whois-api-llc/ipgeo-community" \
      org.opencontainers.image.licenses="CC-BY-SA-4.0"

# tini as PID 1: forwards SIGTERM so `docker stop` exits promptly and clean
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/update.sh"]
