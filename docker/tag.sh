#!/bin/bash

set -e

VERSION="`cif-router --version`"
IMAGES="cif-base cif-router csirtg-fm cif-enricher cif-hunter cif-httpd"

if [[ ${VERSION} == "" ]]; then
    echo "missing version arg..."
    exit;
fi

if [[ "${VERSION}" =~ 'dirty' || "${VERSION}" =~ 'untagged' ]]; then
  VERSION='5.0-test'
fi

for img in ${IMAGES}
do
    docker tag csirtgadgets/${img}:latest csirtgadgets/${img}:${VERSION}
done
