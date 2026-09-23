# Data Strategy & Dataset Governance

## 1. Ground Truth & Core Data Policy

Heavy machine telematics, site environmental data, and operator behavioral datasets provided in hackathon settings are inherently limited in sample size and operational variance.

To maintain engineering integrity, prevent data leakage, and ensure reproducibility:

1. **Untouched Raw Data (`data/raw/`)**:
   - The challenge source data is immutable and read-only.
   - Raw files must never be edited, renamed, or modified in place.
   - Any script reading from `data/raw/` must treat it strictly as read-only.

2. **Processed & Cleaned Data (`data/processed/`)**:
   - Stores standardized tabular data (Parquet or CSV) produced by deterministic cleaning scripts.
   - Handles missing values, unit standardization (metric: km/h, Celsius, tons, kPa), and timestamp normalization to UTC ISO 8601.

3. **Synthetic Expansion (`data/synthetic/`)**:
   - Synthetically expanded datasets to represent edge cases and operational regimes underrepresented in small raw samples.
   - Every synthetic generation run must be deterministic, documented, seeded, and reproducible via scripts in `services/operations/`.

4. **Rigorous Evaluation Splits (`data/evaluation/`)**:
   - Pre-split benchmark datasets: `train.csv`, `val.csv`, `test.csv`, and `edge_cases.csv`.
   - Edge cases explicitly test safety anomalies: abrupt seatbelt unbuckling at speed, proximity sensor failure, sudden coolant thermal spikes, and excessive idle loops.

5. **Honest Modeling Claims**:
   - **Never claim production-level ML accuracy from small hackathon sample data.**
   - All evaluation metrics must clearly articulate sample size, assumptions, confidence intervals, and the baseline heuristic against which the model is evaluated.

---

## 2. Directory Layout & Artifacts

```
data/
├── raw/                 # UNTOUCHED original challenge datasets (read-only)
│   ├── .gitkeep
│   └── README.md
├── processed/           # Standardized, cleaned, schema-validated datasets
│   ├── .gitkeep
│   └── README.md
├── synthetic/           # Documented synthetic expansion for edge cases
│   ├── .gitkeep
│   └── README.md
└── evaluation/          # Fixed splits (train, validation, test, edge cases)
    ├── .gitkeep
    └── README.md
```

---

## 3. Synthetic Data Generation Strategy (Owned by Engineer 2)

Because the hackathon dataset has few anomalies, Engineer 2 generates physics-consistent synthetic telemetry based on known heavy-equipment operating parameters:

1. **Nominal Operating Cycles**:
   - Digging, swinging, dumping, return swing cycles (typical duration: 25-45s for hydraulic excavators).
   - Expected engine RPM: 1600 - 2100 RPM under load; 800 - 1000 RPM idle.

2. **Excessive Idling Scenarios**:
   - Engine running at low RPM (>15 minutes continuous) with zero hydraulic pressure delta.
   - Key flag: `idle_duration_minutes > threshold_minutes`.

3. **Proximity & Collision Hazard Injection**:
   - Dynamic LiDAR/radar proximity telemetry indicating personnel or light vehicles within 2m, 5m, and 10m danger envelopes.

4. **Environmental Degradation Scenarios**:
   - Ground saturation levels increasing grade resistance, degrading cycle times by 10% to 35%.

---

## 4. Evaluation Metrics & Baselines

All machine learning models for ETA prediction and anomaly detection must report:

| Model | Baseline | Target Metric | Minimum Acceptable Threshold |
| :--- | :--- | :--- | :--- |
| **Task ETA Estimator** | Historical median cycle time | Mean Absolute Error (MAE) in minutes | MAE < 15% of total task duration |
| **Excessive Idle Detector**| Fixed 10-minute timer rule | F1-Score on synthetic edge cases | F1 > 0.90 |
| **Unsafe Operation Classifier**| Multi-axis acceleration threshold | Precision / Recall balance | Precision > 0.85, Recall > 0.85 |
