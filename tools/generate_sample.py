#!/usr/bin/env python3
"""Simple sample CSV generator for ad performance data.

Usage:
    python -m tools.generate_sample --output example_inputs/sample.csv --campaigns 10 --days 7 --seed 0

This produces reproducible sample data useful for tests and local benchmarking.
"""
import csv
import random
import argparse
from datetime import date, timedelta

HEADER = ['campaign_id','date','impressions','clicks','spend','conversions']

def generate_sample(path, num_campaigns=10, days=7, seed=0):
    random.seed(seed)
    start = date(2025, 1, 1)
    campaigns = [f"CMP{str(i+1).zfill(3)}" for i in range(num_campaigns)]
    rows = []
    for c in campaigns:
        for d in range(days):
            impressions = random.randint(100, 100000)
            # clicks roughly proportional, but allow variability
            clicks = min(impressions, int(impressions * random.uniform(0.0001, 0.1)))
            spend = round(random.uniform(0.01, 5.0) * clicks, 2)
            conversions = random.randint(0, max(1, clicks // 10))
            rows.append([c, (start + timedelta(days=d)).isoformat(), impressions, clicks, f"{spend:.2f}", conversions])
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', '-o', default='example_inputs/sample.csv', help='Path to write sample CSV (default: example_inputs/sample.csv)')
    p.add_argument('--campaigns', type=int, default=10)
    p.add_argument('--days', type=int, default=7)
    p.add_argument('--seed', type=int, default=0)
    args = p.parse_args()
    generate_sample(args.output, args.campaigns, args.days, args.seed)
