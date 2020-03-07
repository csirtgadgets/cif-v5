FROM csirtgadgets/cif-router:latest

RUN apt-get update && apt-get install -y --no-install-recommends geoipupdate cron

COPY docker/cif-enricher/cron_geoip.sh /etc/cron.monthly/geoip_update.sh

COPY docker/cif-enricher/entrypoint /

RUN apt-get clean \
    && rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT /entrypoint -n
