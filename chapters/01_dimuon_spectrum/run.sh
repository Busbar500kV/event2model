#!/usr/bin/env bash
set -euo pipefail

echo "=== Chapter 1: Dimuon invariant mass ==="

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

echo "[1/5] Pulling latest code..."
git pull

echo "[2/5] Activating virtual environment..."
if [ ! -d ".venv" ]; then
  echo "ERROR: .venv not found. Create it once with:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install numpy pandas matplotlib pyyaml"
  exit 1
fi
source .venv/bin/activate

echo "[3/5] Fetching data (idempotent)..."
DATA_DIR="data_cache/01_dimuon_spectrum"
CSV="${DATA_DIR}/Dimuon_DoubleMu.csv"
URL="http://cern.ch/opendata/record/545/files/Dimuon_DoubleMu.csv"

mkdir -p "${DATA_DIR}"
if [ ! -f "${CSV}" ]; then
  echo "Downloading ${CSV}"
  curl -L --fail -o "${CSV}.tmp" "${URL}"
  mv "${CSV}.tmp" "${CSV}"
else
  echo "Data already present: ${CSV}"
fi

echo "[4/5] Running analysis..."
python chapters/01_dimuon_spectrum/src/run.py \
  --config chapters/01_dimuon_spectrum/config.yaml

echo "[5/5] Publishing results..."
git add chapters/01_dimuon_spectrum/out/results.md chapters/01_dimuon_spectrum/out/metrics.json
git commit -m "Chapter 1: dimuon invariant mass results" || echo "No changes to commit"
git push

echo "=== Chapter 1 completed successfully ==="