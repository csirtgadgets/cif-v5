FROM csirtgadgets/cif-router:latest

COPY fm_requirements.txt /tmp/
RUN pip3 install -r /tmp/fm_requirements.txt

COPY rules*/*.yml /etc/cif/rules/default/
COPY docker/csirtg-fm/entrypoint /

VOLUME /etc/cif/rules/default
VOLUME /var/lib/cif
VOLUME /var/lib/fm
VOLUME /var/log/cif
VOLUME /home/cif

WORKDIR /home/cif

ENTRYPOINT /entrypoint -n
