import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def invariant_mass(E, px, py, pz):
    return np.sqrt(np.maximum(
        (E.sum(axis=1))**2 -
        (px.sum(axis=1))**2 -
        (py.sum(axis=1))**2 -
        (pz.sum(axis=1))**2,
        0
    ))

def run_analysis(cfg):
    data_dir = Path(cfg["paths"]["data_dir"])
    out_dir = Path(cfg["paths"]["out_dir"])
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # load first CSV found
    csv_file = list(data_dir.glob("*.csv"))[0]
    df = pd.read_csv(csv_file)

    E = df[["E1", "E2"]].values
    px = df[["px1", "px2"]].values
    py = df[["py1", "py2"]].values
    pz = df[["pz1", "pz2"]].values

    m_calc = invariant_mass(E, px, py, pz)
    m_given = df["M"].values
    residuals = m_calc - m_given

    # plot invariant mass
    plt.figure(figsize=(8,5))
    plt.hist(m_calc, bins=cfg["plots"]["bins"], range=cfg["plots"]["mass_range"])
    plt.xlabel("Invariant Mass [GeV]")
    plt.ylabel("Events")
    plt.title("Dimuon Invariant Mass Spectrum")
    plt.savefig(fig_dir / "mass_spectrum.png")
    plt.close()

    # residuals
    plt.figure(figsize=(8,5))
    plt.hist(residuals, bins=200)
    plt.xlabel("M_calc − M_given [GeV]")
    plt.ylabel("Events")
    plt.title("Invariant Mass Residuals")
    plt.savefig(fig_dir / "mass_residuals.png")
    plt.close()

    metrics = {
        "events": len(df),
        "residual_rms": float(np.std(residuals)),
        "residual_mean": float(np.mean(residuals))
    }

    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return {
        "metrics": metrics,
        "figures": [
            "mass_spectrum.png",
            "mass_residuals.png"
        ]
    }