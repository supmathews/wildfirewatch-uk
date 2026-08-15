# Decisions

Record project assumptions and architectural decisions here.

## 2026-08-15 — Start with retrospective PoC

The first deliverable is a reproducible retrospective dataset and baseline analysis, not live public alerting or emergency guidance.

## 2026-08-15 — Keep LLMs out of numerical risk scoring

LLMs may help with incident extraction, data-quality summaries, and explanations generated from structured model outputs. They must not be the numerical wildfire-risk model.

## 2026-08-15 — Treat Scotland as a geographic-transfer experiment

The updated landscape review identified close Scotland-specific ML wildfire occurrence/susceptibility work from CEDA / NCAS / University of St Andrews / DTU collaborators. WildfireWatch UK should not assume that England/Wales-trained weather/dryness signals transfer cleanly to Scotland. Scotland should be treated as a formal transfer/calibration experiment once enough Scottish source-backed positives exist, with explicit land-cover, terrain, vegetation and human-activity features.
