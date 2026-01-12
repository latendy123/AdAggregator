# Ad Performance Aggregator

## Overview
CLI tool that aggregates ad performance CSV data by `campaign_id` and outputs:
- `top10_ctr.csv` — top campaigns by CTR (highest)
- `top10_cpa.csv` — top campaigns by lowest CPA (excludes zero-conversion campaigns)

### CSV schema (input)
campaign_id,date,impressions,clicks,spend,conversions

## Setup
Recommended: Python 3.10+

1. Clone repo
2. (Optional) Create virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage
Run the aggregator on a CSV file and write results to an output directory:

### Extract and move ad_data.csv to inputs folder
```bash
python aggregator.py --input inputs/ad_data.csv --output results/ --top 10
```

Where `ad_data.csv` follows the schema: `campaign_id,date,impressions,clicks,spend,conversions`.

## Sample data generator
A helper script is available to generate synthetic sample CSV files for testing (default output is `example_inputs/sample.csv`):

```bash
python -m tools.generate_sample --output example_inputs/sample.csv --campaigns 100 --days 30 --seed 0
```

## Tests
Run the unit tests (requires `pytest`):

```bash
pip install -r requirements.txt
pytest -q
```

## Notes on performance & correctness
- Aggregation is streamed from the CSV; only per-campaign aggregates are held in memory (memory ~ O(number of campaigns)).
- Top-N selection uses heap-based algorithms for performance on large campaign counts and deterministic tie-breakers for reproducible outputs.

## Benchmarking
- A local benchmark runner is available at `tools/benchmark.py`. It can optionally generate a sample CSV and will record elapsed time and peak memory (if `psutil` is installed) to `bench_results/benchmark.log`.

Runtime profiling and a faster numeric mode
- You can get a simple timing report for phases with the `--profile` flag:

```bash
python aggregator.py --input example_inputs/sample_small.csv --output results --top 10 --profile
```

- The aggregator now uses floating-point accumulation (fast mode) by default for improved runtime; this may introduce very minor numeric precision differences compared to arbitrary-precision Decimal. Use `--profile` to capture phase timings when benchmarking.

```bash
python aggregator.py --input example_inputs/sample_small.csv --output results --top 10 --profile
```

Local usage example:

```bash
python -m tools.benchmark --generate --campaigns 200 --days 365 --output bench_results
cat bench_results/benchmark.log
```

- A GitHub Actions workflow (`.github/workflows/benchmark.yml`) runs a larger benchmark on push to `main` and on-demand via `workflow_dispatch`. It generates `example_inputs/sample.csv`, runs the aggregator under `/usr/bin/time -v` and uploads `benchmark.log` and result CSVs as artifacts.

## Files added/changed
- `tools/generate_sample.py` — reproducible sample CSV generator
- `tools/benchmark.py` — local benchmark runner
- `tests/test_cli.py` — end-to-end CLI smoke test
- `.github/workflows/benchmark.yml` — CI benchmark workflow

## Next steps (optional)
- Consider recording and committing a sample `benchmarks/` log for reference in the repo.
- Consider using `float`-based accumulation plus `math.fsum` if Decimal performance becomes a bottleneck; kept `Decimal` here for numeric safety.
