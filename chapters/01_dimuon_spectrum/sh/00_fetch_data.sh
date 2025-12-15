#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="data_cache/01_dimuon_spectrum"
CSV_PATH="${DATA_DIR}/Dimuon_DoubleMu.csv"
URL="http://cern.ch/opendata/record/545/files/Dimuon_DoubleMu.csv"

mkdir -p "${DATA_DIR}"

echo "Downloading Dimuon_DoubleMu.csv into ${CSV_PATH}"
curl -L --fail -o "${CSV_PATH}.tmp" "${URL}"
mv "${CSV_PATH}.tmp" "${CSV_PATH}"

echo "Validating header..."
head -n 1 "${CSV_PATH}" | grep -q "Run,Event" || {
  echo "ERROR: Downloaded file does not look like the expected CSV."
  echo "First 5 lines:"
  head -n 5 "${CSV_PATH}"
  exit 1
}

echo "Done."
ls -lh "${CSV_PATH}"