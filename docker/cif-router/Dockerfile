FROM csirtgadgets/cif-base:latest
LABEL developer="Wes Young <wes@csirtgadgets.com>"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential

RUN mv /etc/ssl/openssl.cnf /etc/ssl/openssl.cnf.orig
RUN sed 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/' /etc/ssl/openssl.cnf.orig > /etc/ssl/openssl.cnf

COPY *requirements.txt /tmp/
COPY docker/cif-router/entrypoint /
COPY rules/* /etc/cif/rules/default/

RUN pip3 install -r /tmp/requirements.txt

RUN if [ -e /tmp/local_requirements.txt ] ; then pip3 install --no-cache-dir -r /tmp/local_requirements.txt ; fi

COPY dist/cif-5*.tar.gz /tmp/cif-v5.tar.gz
RUN mkdir /tmp/cif-v5 \
    && cd /tmp \
    && tar -zxvf /tmp/cif-v5.tar.gz --strip-components=1 -C /tmp/cif-v5

WORKDIR /tmp/cif-v5

RUN CIF_ENABLE_INSTALL=1 python3 setup.py install

VOLUME /var/lib/cif
VOLUME /var/lib/fm
VOLUME /var/log/cif
VOLUME /home/cif

WORKDIR /home/cif

EXPOSE 5555

RUN apt-get remove build-essential -y \
    && apt-get clean && apt-get autoremove -y \
    && rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/cif-v5

ENTRYPOINT /entrypoint -n