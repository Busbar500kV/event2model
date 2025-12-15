import json
import re
import csv
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless-safe (no display needed)
import matplotlib.pyplot as plt


def invariant_mass(E, px, py, pz):
    E_sum = E.sum(axis=1)
    px_sum = px.sum(axis=1)
    py_sum = py.sum(axis=1)
    pz_sum = pz.sum(axis=1)
    m2 = E_sum**2 - px_sum**2 - py_sum**2 - pz_sum**2
    return np.sqrt(np.maximum(m2, 0.0))


def find_csv_file(data_dir: Path) -> Path:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        csv_files = list(data_dir.glob("*/*.csv"))

    if not csv_files:
        found = [str(p.relative_to(data_dir)) for p in data_dir.rglob("*")]
        raise FileNotFoundError(
            f"No CSV files found in {data_dir}.\nFiles present:\n" + "\n".join(found[:50])
        )
    return sorted(csv_files)[0]


def _sniff_delimiter(sample_text: str) -> str:
    candidates = [",", ";", "\t", "|"]
    counts = {c: sample_text.count(c) for c in candidates}
    best = max(counts, key=counts.get)
    if counts[best] > 0:
        return best
    try:
        dialect = csv.Sniffer().sniff(sample_text, delimiters="".join(candidates))
        return dialect.delimiter
    except Exception:
        return ","


def _detect_header_line(lines: list[str]) -> int:
    required = ["E1", "px1", "py1", "pz1", "E2", "px2", "py2", "pz2", "M"]
    for i, ln in enumerate(lines):
        hit = sum(1 for k in required if k in ln)
        if hit >= 5:
            return i
    for i, ln in enumerate(lines):
        if any(d in ln for d in [",", ";", "\t", "|"]) and re.search(r"[A-Za-z]", ln):
            return i
    return 0


def load_table_robust(csv_path: Path) -> pd.DataFrame:
    with open(csv_path, "r", errors="replace") as f:
        first_lines = []
        for _ in range(80):
            try:
                first_lines.append(next(f))
            except StopIteration:
                break
    first_lines = [ln.rstrip("\n") for ln in first_lines if ln is not None]

    header_idx = _detect_header_line(first_lines)
    sample_for_sniff = "\n".join(first_lines[header_idx:header_idx + 20])
    delim = _sniff_delimiter(sample_for_sniff)

    df = pd.read_csv(
        csv_path,
        sep=delim,
        header=0,
        skiprows=header_idx,
        engine="python",
        on_bad_lines="skip",
    )
    df.columns = [c.strip() for c in df.columns]
    return df


def _plot_hist(masses, bins, xlim, outpath, title, log=False):
    plt.figure(figsize=(8, 5))
    plt.hist(masses, bins=bins, range=xlim, histtype="step", log=log)
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events" + (" (log)" if log else ""))
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def _plot_zoom(masses, xlim, outpath, title, bins=120, log=False):
    plt.figure(figsize=(8, 5))
    plt.hist(masses, bins=bins, range=xlim, histtype="step", log=log)
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events" + (" (log)" if log else ""))
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def run_analysis(cfg):
    data_dir = Path(cfg["paths"]["data_dir"])
    out_dir = Path(cfg["paths"]["out_dir"])
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_file = find_csv_file(data_dir)
    print(f"Loading data from: {csv_file}")

    df = load_table_robust(csv_file)
    df = df.dropna(axis=1, how="all")

    required_cols = ["E1", "px1", "py1", "pz1", "E2", "px2", "py2", "pz2", "M"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}\nColumns found: {list(df.columns)}")

    for c in required_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    before = len(df)
    df = df.dropna(subset=required_cols)
    after = len(df)
    if after == 0:
        raise ValueError("After numeric coercion, no valid rows remained.")
    if after < before:
        print(f"Dropped {before - after} rows due to non-numeric/NaN required fields.")

    E = df[["E1", "E2"]].values
    px = df[["px1", "px2"]].values
    py = df[["py1", "py2"]].values
    pz = df[["pz1", "pz2"]].values

    m_calc = invariant_mass(E, px, py, pz)
    m_given = df["M"].values
    residuals = m_calc - m_given

    mass_range = cfg["plots"]["mass_range"]
    bins = cfg["plots"]["bins"]

    _plot_hist(m_calc, bins, mass_range, fig_dir / "mass_spectrum.png",
               "Dimuon Invariant Mass Spectrum", log=False)
    _plot_hist(m_calc, bins, mass_range, fig_dir / "mass_spectrum_log.png",
               "Dimuon Invariant Mass Spectrum (log scale)", log=True)

    plt.figure(figsize=(8, 5))
    plt.hist(residuals, bins=200, histtype="step")
    plt.xlabel("M_calc − M_given [GeV]")
    plt.ylabel("Events")
    plt.title("Invariant Mass Residuals")
    plt.tight_layout()
    plt.savefig(fig_dir / "mass_residuals.png")
    plt.close()

    _plot_zoom(m_calc, (2.8, 3.4), fig_dir / "mass_zoom_jpsi.png",
               "Zoom: J/ψ region (2.8–3.4 GeV)")
    _plot_zoom(m_calc, (9.0, 11.0), fig_dir / "mass_zoom_upsilon.png",
               "Zoom: ϒ region (9–11 GeV)")
    _plot_zoom(m_calc, (80.0, 100.0), fig_dir / "mass_zoom_z.png",
               "Zoom: Z region (80–100 GeV)")

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
            "mass_zoom_jpsi.png",
            "mass_zoom_upsilon.png",
            "mass_zoom_z.png",
        ],
    }