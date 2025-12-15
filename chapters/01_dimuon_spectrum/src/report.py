from pathlib import Path
from datetime import datetime

def write_report(cfg, results):
    out_dir = Path(cfg["paths"]["out_dir"])
    fig_dir = out_dir / "figures"

    lines = []
    lines.append(f"# Chapter 1 — Dimuon Invariant Mass\n")
    lines.append(f"_Generated on {datetime.utcnow().isoformat()} UTC_\n")

    lines.append("## Summary\n")
    lines.append(f"- Events analyzed: **{results['metrics']['events']}**")
    lines.append(f"- Residual RMS: **{results['metrics']['residual_rms']:.3e} GeV**\n")

    lines.append("## Figures\n")
    for fig in results["figures"]:
        lines.append(f"![{fig}](figures/{fig})")

    lines.append("\n## Interpretation\n")
    lines.append(
        "Resonant structure appears only after aggregating many events. "
        "Invariant mass is not an event-level property but a statistical construct "
        "derived from Lorentz-invariant constraints."
    )

    with open(out_dir / "results.md", "w") as f:
        f.write("\n".join(lines))