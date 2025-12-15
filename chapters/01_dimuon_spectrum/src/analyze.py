import json
import re
import csv
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def invariant_mass(E, px, py, pz):
    """
    Compute invariant mass from two-particle four-vectors.
    Inputs are arrays of shape (N, 2).
    """
    E_sum = E.sum(axis=1)
    px_sum = px.sum(axis=1)
    py_sum = py.sum(axis=1)
    pz_sum = pz.sum(axis=1)

    m2 = E_sum**2 - px_sum**2 - py_sum**2 - pz_sum**2
    return np.sqrt(np.maximum(m2, 0.0))


def find_csv_file(data_dir: Path) -> Path:
    """
    Locate a CSV file in data_dir or its immediate subdirectories.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        csv_files = list(data_dir.glob("*/*.csv"))

    if not csv_files:
        found = [str(p.relative_to(data_dir)) for p in data_dir.rglob("*")]
        raise FileNotFoundError(
            f"No CSV files found in {data_dir}.\n"
            f"Files present:\n" + "\n".join(found[:50])
        )

    return sorted(csv_files)[0]


def _sniff_delimiter(sample_text: str) -> str:
    """
    Sniff delimiter from a sample. Fall back to comma.
    """
    candidates = [",", ";", "\t", "|"]
    # Quick heuristic first
    counts = {c: sample_text.count(c) for c in candidates}
    best = max(counts, key=counts.get)
    if counts[best] > 0:
        return best

    # csv.Sniffer fallback
    try:
        dialect = csv.Sniffer().sniff(sample_text, delimiters="".join(candidates))
        return dialect.delimiter
    except Exception:
        return ","


def _detect_header_line(lines: list[str]) -> int:
    """
    Find the most likely header line index.
    We prefer a line that contains the required column names.
    Otherwise we choose the first line that looks "table-like" (has delimiters).
    """
    required = ["E1", "px1", "py1", "pz1", "E2", "px2", "py2", "pz2", "M"]

    # First pass: line contains multiple required tokens
    for i, ln in enumerate(lines):
        hit = sum(1 for k in required if k in ln)
        if hit >= 5:  # strong signal: at least 5 required columns named
            return i

    # Second pass: line looks like delimited header (has letters + delimiter)
    for i, ln in enumerate(lines):
        if any(d in ln for d in [",", ";", "\t", "|"]) and re.search(r"[A-Za-z]", ln):
            return i

    # Fallback: assume first line is header
    return 0


def load_table_robust(csv_path: Path) -> pd.DataFrame:
    """
    Robust loader for CERN Open Data 'CSV' files that may include:
    - metadata lines before header
    - non-comma delimiters
    - quoting oddities that break pandas C-engine
    """
    # Read a small chunk of lines to detect header + delimiter
    with open(csv_path, "r", errors="replace") as f:
        first_lines = [next(f) for _ in range(80)]  # may raise StopIteration for tiny files
    # If file shorter than 80 lines
    first_lines = [ln.rstrip("\n") for ln in first_lines if ln is not None]

    header_idx = _detect_header_line(first_lines)
    sample_for_sniff = "\n".join(first_lines[header_idx:header_idx + 20])
    delim = _sniff_delimiter(sample_for_sniff)

    # Try robust pandas read
    try:
        df = pd.read_csv(
            csv_path,
            sep=delim,
            header=0,
            skiprows=header_idx,
            engine="python",         # robust against irregular quoting
            on_bad_lines="skip",     # skip any garbage lines
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to parse {csv_path} with delimiter '{delim}' and header at line {header_idx}.\n"
            f"Original error: {e}"
        )

    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    return df


def run_analysis(cfg):
    data_dir = Path(cfg["paths"]["data_dir"])
    out_dir = Path(cfg["paths"]["out_dir"])
    fig_dir = out_dir / "figures"

    fig_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------
    csv_file = find_csv_file(data_dir)
    print(f"Loading data from: {csv_file}")

    df = load_table_robust(csv_file)

    # Some files may include unnamed columns or empties; drop fully-empty columns
    df = df.dropna(axis=1, how="all")

    required_cols = ["E1", "px1", "py1", "pz1",
                     "E2", "px2", "py2", "pz2", "M"]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Columns found: {list(df.columns)}"
        )

    # Ensure numeric (coerce non-numeric to NaN, then drop)
    for c in required_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    before = len(df)
    df = df.dropna(subset=required_cols)
    after = len(df)
    if after == 0:
        raise ValueError("After numeric coercion, no valid rows remained. Check the CSV formatting.")
    if after < before:
        print(f"Dropped {before - after} rows due to non-numeric/NaN required fields.")

    # --------------------------------------------------
    # Reconstruct invariant mass
    # --------------------------------------------------
    E = df[["E1", "E2"]].values
    px = df[["px1", "px2"]].values
    py = df[["py1", "py2"]].values
    pz = df[["pz1", "pz2"]].values

    m_calc = invariant_mass(E, px, py, pz)
    m_given = df["M"].values
    residuals = m_calc - m_given

    # --------------------------------------------------
    # Plots
    # --------------------------------------------------
    mass_range = cfg["plots"]["mass_range"]
    bins = cfg["plots"]["bins"]

    # Spectrum (linear)
    plt.figure(figsize=(8, 5))
    plt.hist(m_calc, bins=bins, range=mass_range, histtype="step")
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events")
    plt.title("Dimuon Invariant Mass Spectrum")
    plt.tight_layout()
    plt.savefig(fig_dir / "mass_spectrum.png")
    plt.close()

    # Spectrum (log)
    plt.figure(figsize=(8, 5))
    plt.hist(m_calc, bins=bins, range=mass_range, histtype="step", log=True)
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events (log)")
    plt.title("Dimuon Invariant Mass Spectrum (log scale)")
    plt.tight_layout()
    plt.savefig(fig_dir / "mass_spectrum_log.png")
    plt.close()

    # Residuals
    plt.figure(figsize=(8, 5))
    plt.hist(residuals, bins=200, histtype="step")
    plt.xlabel("M_calc − M_given [GeV]")
    plt.ylabel("Events")
    plt.title("Invariant Mass Residuals")
    plt.tight_layout()
    plt.savefig(fig_dir / "mass_residuals.png")
    plt.close()

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------
    metrics = {
        "events": int(len(df)),
        "residual_mean": float(np.mean(residuals)),
        "residual_rms": float(np.std(residuals)),
        "csv_file": str(csv_file),
        "min_mass_calc": float(np.min(m_calc)),
        "max_mass_calc": float(np.max(m_calc)),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return {
        "metrics": metrics,
        "figures": [
            "mass_spectrum.png",
            "mass_spectrum_log.png",
            "mass_residuals.png",
        ],
    }