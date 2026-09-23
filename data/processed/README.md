# Processed Data Directory (`data/processed/`)

## Purpose
This directory contains cleaned, standardized, and validated versions of the raw challenge datasets.

## Governance Standards
- All timestamps converted to ISO 8601 UTC.
- Metric unit normalization (pressure: kPa, speed: km/h, volume: tons, temp: °C).
- Imputation methodologies and outlier clipping must be documented alongside generated files.
- Managed and generated exclusively by **Engineer 2 (Operations & ML)**.
