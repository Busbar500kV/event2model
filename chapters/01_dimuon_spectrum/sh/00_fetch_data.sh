#!/usr/bin/env bash
set -e

RECID=5201
DATA_DIR=data_cache/01_dimuon_spectrum

mkdir -p ${DATA_DIR}

if ! command -v cernopendata-client &> /dev/null; then
  pip install cernopendata-client
fi

echo "Downloading CERN Open Data record ${RECID}"
cernopendata-client download-files \
  --recid ${RECID} \
  --output-directory ${DATA_DIR}

echo "Data downloaded to ${DATA_DIR}"