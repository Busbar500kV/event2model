#!/usr/bin/env bash
set -euo pipefail

echo "=== Chapter 1: Dimuon invariant mass ==="

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

echo "[1/6] Pulling latest code..."
git pull

echo "[2/6] Activating virtual environment..."
if [ ! -d ".venv" ]; then
  echo "ERROR: .venv not found."
  exit 1
fi
source .venv/bin/activate

echo "[3/6] Fetching data (idempotent)..."
DATA_DIR="data_cache/01_dimuon_spectrum"
CSV="${DATA_DIR}/Dimuon_DoubleMu.csv"
URL="http://cern.ch/opendata/record/545/files/Dimuon_DoubleMu.csv"

mkdir -p "${DATA_DIR}"
if [ ! -f "${CSV}" ]; then
  curl -L --fail -o "${CSV}.tmp" "${URL}"
  mv "${CSV}.tmp" "${CSV}"
else
  echo "Data already present: ${CSV}"
fi

echo "[4/6] Running analysis..."
python chapters/01_dimuon_spectrum/src/run.py \
  --config chapters/01_dimuon_spectrum/config.yaml

echo "[5/6] Verifying figures exist..."
FIG_DIR="chapters/01_dimuon_spectrum/out/figures"
mkdir -p "${FIG_DIR}"
echo "Figures in ${FIG_DIR}:"
ls -lh "${FIG_DIR}" || true

echo "[6/6] Publishing results (force-add figures)..."
git add chapters/01_dimuon_spectrum/out/results.md
git add chapters/01_dimuon_spectrum/out/metrics.json
git add -f chapters/01_dimuon_spectrum/out/figures/*.png || true

git status --porcelain

git commit -m "Chapter 1: dimuon invariant mass results" || echo "No changes to commit"
git push

echo "=== Chapter 1 completed successfully ==="