FROM csirtgadgets/cif-router:latest

COPY docker/cif-httpd/entrypoint /

VOLUME /home/cif

WORKDIR /home/cif

ENTRYPOINT /entrypoint -n
