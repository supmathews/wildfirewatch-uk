# Open Issues

- Find a durable source URL for the Tamworth case-study fire; it remains a placeholder record and must not be used for analysis yet.
- Replace approximate geocoded point locations with source-backed incident centroids or fire perimeters before spatial modelling.
- Confirm exact ignition/start times for Stourbridge, New Forest, Porth, and Tamworth.
- Resolve source-backed coordinates for Cannock Chase; the official source names Brocton/Sherbrook Valley but no centroid has been selected.
- Replace the Open-Meteo archive fallback with authoritative UK rainfall/weather providers where licensing and historical coverage allow.
- Add matched non-fire control locations so the first retrospective dataset can test whether incident locations ranked unusually high.
- Add a risk-decay-after-rainfall experiment: snapshot affected/high-risk locations daily for 1-2 weeks and verify risk scores fall credibly after meaningful rain, cooler temperatures, and higher humidity.
- Decide whether to use a 1 km UK grid or H3 cells for the first case study.
