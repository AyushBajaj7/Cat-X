# Evaluation Data Directory (`data/evaluation/`)

## Purpose
This directory stores pre-split train, validation, and test sets used to benchmark model accuracy and edge-case detection.

## Evaluation Protocol
- `train.csv`: Training dataset for task time estimation and normal cycle profiling.
- `val.csv`: Hyperparameter tuning split.
- `test.csv`: Final model performance testing.
- `edge_cases.csv`: Isolated safety hazard test fixtures for evaluating zero false-negative requirements on critical alerts.
- Never claim production-grade ML accuracy from small hackathon sample data.
- Maintained exclusively by **Engineer 2 (Operations & ML)**.
