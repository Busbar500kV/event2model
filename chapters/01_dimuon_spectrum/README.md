# Chapter 1 — Dimuon Invariant Mass

## Objective
Reconstruct the invariant mass spectrum of dimuon events using open LHC data and verify, numerically, how a physical model emerges from detector-level measurements.

This chapter establishes the core pattern used throughout *event2model*: start from events, apply minimal physical structure, and examine what becomes visible.

---

## Dataset
This chapter uses publicly released LHC dimuon collision data containing reconstructed muon kinematics and event-level invariant mass information.

The dataset includes, per event:
- Four-momentum components for two reconstructed muons
- Muon charge
- A provided dimuon invariant mass value

Only minimal preprocessing is applied. No particle identification, fitting, or machine learning is used.

---

## Experiment
1. Load dimuon events.
2. Independently reconstruct the invariant mass from muon four-vectors.
3. Compare the reconstructed mass with the provided invariant mass value.
4. Build invariant mass distributions across all events.
5. Examine the emergence of resonant structure through statistics.

The invariant mass is computed as:

\[
m^2 = (E_1 + E_2)^2 - (\vec{p}_1 + \vec{p}_2)^2
\]

---

## Results
The dimuon invariant mass spectrum exhibits distinct resonant features that are not present at the level of individual events.

Key observations:
- Resonances appear only through aggregation across many events.
- Independent reconstruction of invariant mass agrees with the provided values within numerical precision.
- No single event contains a “particle”; particles appear as statistical structure.

Generated outputs include:
- Full invariant mass spectrum (linear and logarithmic scales)
- Zoomed views of resonance regions
- Residual distribution between reconstructed and provided invariant mass values

---

## Interpretation
This experiment demonstrates that physical objects in collider physics do not exist at the event level.

They emerge as stable patterns constrained by:
- Lorentz-invariant structure
- Conservation laws
- Statistical aggregation

The invariant mass spectrum is therefore not a picture of particles, but a model constructed from measurements.

This chapter establishes the conceptual foundation for all subsequent chapters: **physics begins after events are interpreted, not when they occur.**