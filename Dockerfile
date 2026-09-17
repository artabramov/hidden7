FROM python:3.12-slim
WORKDIR /opt/hidden

RUN apt-get update \
 && apt-get install -y --no-install-recommends gocryptfs fuse3 \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -fsSL \
      https://github.com/versity/versitygw/releases/download/v1.8.0/versitygw_1.8.0_linux_amd64.deb \
      -o /tmp/versitygw.deb \
 && apt-get install -y --no-install-recommends /tmp/versitygw.deb \
 && rm -f /tmp/versitygw.deb \
 && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]