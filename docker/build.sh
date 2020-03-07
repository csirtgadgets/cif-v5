#!/bin/bash

set -e

IMAGES="cif-base cif-router cif-httpd csirtg-fm cif-hunter cif-enricher"

cd ../

for i in ${IMAGES}
do
    docker build --rm=true --force-rm=true -t csirtgadgets/${i} -f docker/${i}/Dockerfile .
done