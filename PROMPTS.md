# PROMPTS.md
Prompt used with Copilot for design + code scaffolding:

1. Prompt: "Help me implement a memory-efficient Python CLI that aggregates a ~1GB CSV with columns
campaign_id,date,impressions,clicks,spend,conversions. It should produce two CSV files:
top10_ctr.csv (top 10 by CTR) and top10_cpa.csv (top 10 lowest CPA, exclude zero conversions).
Show code with a library module for aggregation and a CLI entrypoint. Include unit tests,
Dockerfile, and README. Make CTR formatted to 4 decimals and CPA to 2 decimals."

2. Prompt: "Make a sample input with small data for testing"

3. I run with sample data, It worked! And I run with real data, It still work!. But it take quite a long time to produce results

3. I prompt: "It's working, but it feels like it's taking quite a long time to produce results.
Add a function to check runtime"

4. I ran it with old mode to see execution time:
>> python aggregator.py --input inputs\ad_data.csv --output results_default_run1 --top 10 --profile
```bash Result:
Aggregating file: inputs\ad_data.csv
Found 50 unique campaigns
Wrote top CTR -> results_default_run1\top10_ctr.csv
Wrote top CPA -> results_default_run1\top10_cpa.csv
Timings (seconds):
  aggregate: 45.1927
  compute_metrics: 0.0001
  top_ctr + write: 0.0006
  top_cpa + write: 0.0006
  total: 45.1944
```

5. Prompt: "Is there another way, or a way to optimize the current code, to process and produce output faster?Optimize runtime as best as possible"

I Run the same comparison on the full dataset (ad_data.csv) with --profile to show timing differences between default and --fast
>> python aggregator.py --input inputs\ad_data.csv --output results_fast_run1 --top 10 --fast --profile
```bash Result:
Aggregating file: inputs\ad_data.csv
Found 50 unique campaigns
Wrote top CTR -> results_fast_run1\top10_ctr.csv
Wrote top CPA -> results_fast_run1\top10_cpa.csv
Timings (seconds):
  aggregate: 36.2618
  compute_metrics: 0.0000
  top_ctr + write: 0.0006
  top_cpa + write: 0.0012
  total: 36.2640
```
6. It actually reduced processing time by almost 10 seconds. I could continue prompting for further optimization, but I'll stop here.

7. Prompt: "Fast mode has been enabled and processing time has been reduced; please retain this logic as the default." and I run again to ensure the code continues to function normally.
>> python aggregator.py --input inputs\ad_data.csv --output results_default_run1 --top 10 --profile
