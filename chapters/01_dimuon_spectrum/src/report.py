from pathlib import Path
from datetime import datetime


def write_report(cfg, results):
    out_dir = Path(cfg["paths"]["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = results.get("metrics", {})
    figures = results.get("figures", [])

    ts = datetime.utcnow().isoformat() + " UTC"

    lines = []
    lines.append("# Chapter 1 — Dimuon Invariant Mass")
    lines.append("")
    lines.append(f"_Generated on {ts}_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Events analyzed: **{metrics.get('events', 'N/A')}**")
    rms = metrics.get("residual_rms", None)
    if isinstance(rms, (int, float)):
        lines.append(f"- Residual RMS: **{rms:.3e} GeV**")
    else:
        lines.append(f"- Residual RMS: **{rms}**")
    lines.append("")

    lines.append("## Figures")
    lines.append("")
    for fig in figures:
        lines.append(f"![{fig}](figures/{fig})")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Resonant structure appears only after aggregating many events. "
        "Invariant mass is not an event-level property but a statistical construct "
        "derived from Lorentz-invariant constraints."
    )
    lines.append("")  # final newline

    (out_dir / "results.md").write_text("\n".join(lines), encoding="utf-8")