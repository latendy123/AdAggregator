# example_inputs/

This directory stores small, human-readable sample CSV files used for examples, tests, and local benchmarking.

Conventions:
- Default sample file path: `example_inputs/sample.csv` (used by `tools/generate_sample.py --output` when `--output` is not provided).
- You can put other small sample files here (e.g., `sample_small.csv`) for manual testing or documentation.
- Files must follow the CSV schema: `campaign_id,date,impressions,clicks,spend,conversions`.

Usage examples:
- Generate a sample CSV here:
  ```bash
  python -m tools.generate_sample --output example_inputs/sample.csv --campaigns 100 --days 30 --seed 0
  ```
- Run aggregator on the sample:
  ```bash
  python aggregator.py --input example_inputs/sample.csv --output results --top 10
  ```
