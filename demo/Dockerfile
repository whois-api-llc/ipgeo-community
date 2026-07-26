FROM python:3.12-alpine

# tini as PID 1 so docker stop terminates promptly. Both installs sit above the
# COPY so a code edit doesn't re-fetch them.
RUN apk add --no-cache tini && adduser -D -H app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY app.py .

ENV IPGEO_MMDB=/data/ipgeo-community.mmdb
EXPOSE 8080

USER app
ENTRYPOINT ["/sbin/tini", "--", "python3", "app.py"]
