#!/bin/bash

MACHINE_NAME=cif-httpd
HUNT_SLEEP=90
DONE_SLEEP=90

set -e

rm -rf data/cif/cifv5.db
rm -rf data/fm/fm.db

echo 'giving things a chance to settle...'
sleep 5

echo 'testing query'
docker exec -it -e 'CIF_REMOTE=http://localhost:5000' cif-httpd cif --search example.com

echo 'waiting...'
sleep 5

echo 'testing query'
docker exec -it -e 'CIF_REMOTE=http://localhost:5000' cif-httpd cif --search example.com

echo 'waiting...'
sleep 5

docker exec -it -e 'CIF_REMOTE=http://localhost:5000' cif-httpd cif --itype ipv4 --tags saerch

docker exec -it -e 'CIF_REMOTE=http://localhost:5000' cif-httpd cif -q 93.184.216.34

echo 'waiting...'
sleep 5

docker exec -it -e 'CIF_REMOTE=http://localhost:5000' cif-httpd cif -q 93.184.216.34

declare -a CMDS=(
    "-r /etc/cif/rules/default/alexa.yml"
    "-r /etc/cif/rules/default/openphish.yml"
    "-r /etc/cif/rules/default/openphish.yml"
    "-r /etc/cif/rules/default/csirtg.yml -f csirtgadgets/darknet"
    "-r /etc/cif/rules/default/csirtg.yml -f csirtgadgets/uce-urls"
    "-r /etc/cif/rules/default/phishtank.yml"
)

for i in "${CMDS[@]}"; do
    echo "$i"
    docker exec -it -e CIF_REMOTE='ipc:///var/lib/cif/router.ipc' -e "CSIRTG_TOKEN=${CSIRTG_TOKEN}" \
        csirtg-fm csirtg-fm --client cifzmq -d --limit 100 --skip-invalid \
        --remember --remember-path /tmp/fm.db ${i}
done

echo "waiting ${HUNT_SLEEP}... let hunter do their thing..."
sleep ${HUNT_SLEEP}

declare -a CMDS=(
    "--provider csirtg.io --no-feed --itype url"
    "--provider openphish.com --itype url"
    "--itype ipv4 --tags scanner"
    "--itype ipv4 --tags scanner --days 17"
    "--itype fqdn --tags search"
    "--itype url --tags uce"
    "--itype url --tags phishing"
    "--itype ipv4 --tags phishing --confidence 2"
    "--itype ipv4 --confidence 1,4 --no-feed -d"
    "--itype fqdn --confidence 1,4 --no-feed -d"
    "--itype fqdn --tags phishing --confidence 0"
    "--itype ipv4 --tags phishing --confidence 0"
#    "--indicator csirtg.io --tags malware --submit --confidence 4"
)

for i in "${CMDS[@]}"; do
    echo "$i"
    docker exec -e 'CIF_REMOTE=http://localhost:5000' -e CIF_EXPERT=1 -it ${MACHINE_NAME} cif ${i}
done

echo "testing bulk search"

cat bulk.txt | docker exec -e 'CIF_REMOTE=http://localhost:5000' -e CIF_EXPERT=1 -i ${MACHINE_NAME} cif

sleep 1

cat bulk.txt | docker exec -e 'CIF_REMOTE=http://localhost:5000' -e CIF_EXPERT=1 -i ${MACHINE_NAME} cif

docker exec -e 'CIF_REMOTE=http://localhost:5000' -it ${MACHINE_NAME} cif -q '5.5.5.5,6.6.6.6'

sleep 1

docker exec -e 'CIF_REMOTE=http://localhost:5000' -it ${MACHINE_NAME} cif -q '5.5.5.5,6.6.6.6'

echo "done..."

sleep ${DONE_SLEEP}

