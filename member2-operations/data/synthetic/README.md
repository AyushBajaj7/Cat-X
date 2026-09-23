# Synthetic Data Directory (`data/synthetic/`)

## Purpose
This directory contains deterministic, physics-informed synthetic telemetry and operational logs.

## Synthetic Expansion Policy
Because the hackathon raw dataset provides limited anomaly examples:
- Synthetic edge cases are generated with fixed seeds (`random_state=42`).
- Scenarios modeled include: abrupt seatbelt unbuckling during high RPM, rapid hydraulic pressure collapse, obstacle proximity breach at speed, and persistent excessive idling (>15 mins).
- All synthetic datasets must clearly include the column `is_synthetic: true` to prevent leakage into non-synthetic benchmarks.
- Maintained exclusively by **Engineer 2 (Operations & ML)**.
