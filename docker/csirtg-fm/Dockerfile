FROM csirtgadgets/cif-router:latest

COPY fm_requirements.txt /tmp/
RUN pip3 install -r /tmp/fm_requirements.txt

COPY rules*/*.yml /etc/cif/rules/
RUN chmod 750 /etc/cif/rules && chmod 640 /etc/cif/rules/* && chown -R cif:cif /etc/cif

COPY docker/csirtg-fm/entrypoint /

VOLUME /etc/cif/rules/default
VOLUME /etc/cif/rules/local
VOLUME /var/lib/cif
VOLUME /var/lib/fm
VOLUME /var/log/cif
VOLUME /home/cif

WORKDIR /home/cif

ENTRYPOINT /entrypoint -n
