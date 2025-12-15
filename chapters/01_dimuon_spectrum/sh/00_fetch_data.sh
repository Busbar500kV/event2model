#!/usr/bin/env bash
set -euo pipefail

RECID=5201
DATA_DIR="data_cache/01_dimuon_spectrum"

mkdir -p "${DATA_DIR}"

if ! command -v cernopendata-client &> /dev/null; then
  pip install cernopendata-client
fi

echo "Downloading CERN Open Data record ${RECID} into ${DATA_DIR}"

# cernopendata-client writes into the current working directory in some versions
pushd "${DATA_DIR}" > /dev/null
cernopendata-client download-files --recid "${RECID}"
popd > /dev/null

echo "Done. Listing CSV files:"
ls -lh "${DATA_DIR}"/*.csv 2>/dev/null || echo "No CSV files found yet in ${DATA_DIR}"