# External wildfire-forecasting repo review — lessons, not code

Reviewed after PR #10, following the updated landscape findings and Mat's explicit instruction:

> understand the tech, but do not copy the code at any point.

## Repo reviewed

- Repository: `ECMWFCode4Earth/wildfire-forecasting`
- URL: https://github.com/ECMWFCode4Earth/wildfire-forecasting
- Licence observed via GitHub metadata: GPL-3.0
- Review mode: high-level architecture and documentation only; no code copied into WildfireWatch UK.

## What it appears to do

The repo aims to reproduce/benchmark fire-danger forecasting capabilities using deep learning, especially U-Net-style spatial models over gridded fire-weather / reanalysis / FRP-style data. It includes:

- general train/test/plot scripts;
- modular dataloader classes for forecast/reanalysis/FRP data;
- model modules for several U-Net variants;
- configuration-driven experiments;
- notebooks and documentation for inference/case studies;
- pre-trained-model artefacts and visual metric outputs.

## Lessons for WildfireWatch UK

These are conceptual lessons only:

1. **Keep data loading modular.** WildfireWatch should keep providers and feature builders swappable: Open-Meteo fallback today, FWI/PoF/FireInSite/UKCEH-style features later.
2. **Use configuration for experiments.** Control type, feature families, lookback windows and evaluation splits should be explicit parameters, not hidden constants.
3. **Separate train, evaluate and report scripts.** This matches WildfireWatch's current scripts/reports pattern and should continue.
4. **Support case-study diagnostics.** Small case-study reports are useful while data volume is tiny, but must be clearly labelled as diagnostic.
5. **Benchmark against established danger products.** The reviewed repo's GEFF/FWI benchmarking reinforces the updated landscape recommendation: compare WildfireWatch occurrence ranking against FWI/PoF-style baselines when available.
6. **Avoid random splits.** WildfireWatch should continue moving toward temporal/geographic/incident-group holdouts rather than row-random validation.

## What not to copy

- No model architecture code.
- No dataloader implementation code.
- No training loop or configuration code.
- No GPL-derived implementation details.

## Implication for next WildfireWatch PR

The next useful implementation remains local to WildfireWatch's own design: cached/throttled OSM land-cover classification, land-cover-matched control generation, and a spatial leave-one-incident-out rerun. That tests whether the promising temporal-control signal survives a harder but fairer spatial comparison.
