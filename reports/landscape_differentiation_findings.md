# Landscape and differentiation findings

Source document: `WildfireWatch_UK_Landscape_Findings.pdf`, received 15 August 2026.

## Summary

The landscape scan did not find a closely matching public UK project combining AI-assisted ignition-risk scoring, retrospective fire-vs-control validation, SHAP-style explanations, and a UK wildfire situational-intelligence dashboard.

Closest related work includes:

- **FireInSite**: UK fire-behaviour prediction after ignition; focused on spread/intensity/flame behaviour rather than pre-ignition ranking.
- **Met Office / Natural England Fire Severity Index**: established traditional severity/risk index layers.
- **EFFIS**: European satellite hotspot/danger monitoring.
- **ECMWF Probability of Fire**: global active-fire probability model, not a UK-specific open retrospective PoC.
- **Academic work**: UK susceptibility mapping, infrastructure exposure, and burned-area detection.

## WildfireWatch UK differentiation to preserve

- Retrospective, leakage-safe question: were recent wildfire locations unusually high-risk **before** ignition relative to matched non-fire controls?
- 1 km / H3-style ignition-risk scoring with calibrated bands.
- Multi-window dryness features: 24h, 7d, 30d, 60d, 90d, days since meaningful rain, and consecutive dry days.
- Strict provenance for incident facts, coordinates, and source timestamps.
- Clear separation between ignition risk, potential severity, satellite detections, and incident status.
- SHAP-style “Why Here?” explanations later, with constrained natural language and no invented causes.
- Experimental decision-support positioning, not an official emergency-warning or evacuation-advice system.

## Build implication

Continue prioritising the proof path:

1. Improve positive incident coverage.
2. Improve matched controls.
3. Generate leakage-safe pre-ignition features.
4. Evaluate Recall@TopX%, PR-AUC, ROC-AUC when the dataset is large enough.
5. Only invest heavily in dashboard/UI after predictive value is demonstrated.
