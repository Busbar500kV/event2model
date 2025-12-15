import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


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
    Fail loudly and informatively if none are found.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    # Look for CSVs at top level
    csv_files = list(data_dir.glob("*.csv"))

    # If none found, look one level deeper
    if not csv_files:
        csv_files = list(data_dir.glob("*/*.csv"))

    if not csv_files:
        found = [str(p.relative_to(data_dir)) for p in data_dir.rglob("*")]
        raise FileNotFoundError(
            f"No CSV files found in {data_dir}.\n"
            f"Files present:\n" + "\n".join(found[:30])
        )

    return sorted(csv_files)[0]


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

    df = pd.read_csv(csv_file)

    required_cols = ["E1", "px1", "py1", "pz1",
                     "E2", "px2", "py2", "pz2", "M"]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

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

    # Invariant mass spectrum (linear)
    plt.figure(figsize=(8, 5))
    plt.hist(m_calc, bins=bins, range=mass_range, histtype="step")
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events")
    plt.title("Dimuon Invariant Mass Spectrum")
    plt.tight_layout()
    plt.savefig(fig_dir / "mass_spectrum.png")
    plt.close()

    # Invariant mass spectrum (log-y)
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
        "csv_file": str(csv_file)
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # --------------------------------------------------
    # Return summary for report
    # --------------------------------------------------
    return {
        "metrics": metrics,
        "figures": [
            "mass_spectrum.png",
            "mass_spectrum_log.png",
            "mass_residuals.png"
        ]
    }