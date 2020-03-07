#!/bin/bash

set -e

VERSION="`cif --version`"
IMAGES="cif-base cif-router csirtg-fm cif-enricher cif-hunter cif-httpd"

if [[ ${VERSION} == "" ]]; then
    echo "missing version arg..."
    exit;
fi

for img in ${IMAGES}
do
    docker push csirtgadgets/${img}:latest
    docker push csirtgadgets/${img}:${VERSION}
done
