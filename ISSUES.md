# Open Issues

- Find a durable source URL for the Tamworth case-study fire; it remains a placeholder record and must not be used for analysis yet.
- Replace approximate geocoded point locations with source-backed incident centroids or fire perimeters before spatial modelling.
- Confirm exact ignition/start times for Stourbridge, New Forest, Porth, and Tamworth.
- Resolve source-backed coordinates for the 30 July Cannock Chase incident; the official source names Brocton/Sherbrook Valley but no centroid has been selected.
- Consider adding the separate 5 August 2026 Cannock Chase / Sherbrook Valley fire as its own seed record; BBC reported a larger fire at about 14:30 BST on Wednesday 5 August.
- Replace the Open-Meteo archive fallback with authoritative UK rainfall/weather providers where licensing and historical coverage allow.
- Before public-facing docs/demos, explicitly position WildfireWatch UK against FireInSite, Met Office/Natural England Fire Severity Index, EFFIS, and ECMWF Probability of Fire without overstating capability.
- Add matched non-fire control locations so the first retrospective dataset can test whether incident locations ranked unusually high.
- Add a risk-decay-after-rainfall experiment: snapshot affected/high-risk locations daily for 1-2 weeks and verify risk scores fall credibly after meaningful rain, cooler temperatures, and higher humidity.
- Decide whether to use a 1 km UK grid or H3 cells for the first case study.
