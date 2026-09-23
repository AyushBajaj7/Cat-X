# Raw Data Directory (`data/raw/`)

## Immutability Policy
This directory stores **untouched, read-only** source datasets provided by Caterpillar for the hackathon.

- **DO NOT** edit, clean, overwrite, or reformat files placed here.
- **DO NOT** commit large raw telemetry binary/parquet dumps into git.
- All processing scripts must read from `data/raw/` in read-only mode and output results exclusively to `data/processed/`.
