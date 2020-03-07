FROM python:3.7-slim-buster
# https://tecadmin.net/install-python-3-8-amazon-linux/
LABEL developer="Wes Young <wes@csirtgadgets.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "deb http://http.debian.net/debian/ buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://http.debian.net/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/ buster/updates main contrib non-free" >> /etc/apt/sources.list

RUN echo "resolvconf resolvconf/linkify-resolvconf boolean false" | debconf-set-selections

# https://hackernoon.com/tips-to-reduce-docker-image-sizes-876095da3b34
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends python3-snappy libsnappy-dev build-essential libmagic-dev

RUN useradd cif

RUN pip3 install ujson~=1.35 pytricia~=1.0 python-snappy~=0.5 maxminddb~=1.5 geoip2~=3.0

RUN apt-get remove build-essential -y \
    && apt-get clean && apt-get autoremove -y \
    && rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/*
