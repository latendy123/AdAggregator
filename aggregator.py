# aggregator.py
import csv
import os
import argparse
from aggregator_lib import aggregate_from_csv_rows, compute_metrics
from typing import List, Tuple
import heapq
from time import perf_counter
import math
import sys

CSV_HEADER = ['campaign_id','total_impressions','total_clicks','total_spend','total_conversions','CTR','CPA']

def write_csv(path: str, rows: List[Tuple]):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for r in rows:
            writer.writerow(r)

def format_row(item) -> List:
    """
    item: (campaign_id, impressions, clicks, spend(Decimal), conversions, ctr(Decimal|None), cpa(Decimal|None))
    Format CTR as 4 decimals (0.0500), CPA & total_spend with 2 decimals
    Use empty string for None values
    """
    cid, impressions, clicks, spend, conversions, ctr, cpa = item
    spend_str = f"{spend:.2f}"
    ctr_str = "" if ctr is None else f"{float(ctr):.4f}"
    cpa_str = "" if cpa is None else f"{float(cpa):.2f}"
    return [cid, impressions, clicks, spend_str, conversions, ctr_str, cpa_str]

def top_n_by_ctr(metrics, n=10):
    """Return top N campaigns by CTR (highest first).

    Excludes campaigns with zero impressions or undefined CTR. The
    result is deterministic: primary sort by CTR descending, secondary
    by campaign_id ascending.
    """
    # Filter out entries without CTR or with zero impressions
    filtered = [m for m in metrics if m[5] is not None and m[1] > 0]
    if not filtered:
        return []
    if len(filtered) <= n:
        # sort by CTR desc then campaign_id asc
        return sorted(filtered, key=lambda x: (-float(x[5]), x[0]))[:n]
    # use heap to efficiently get top N by CTR, then sort deterministically
    top = heapq.nlargest(n, filtered, key=lambda x: float(x[5]))
    return sorted(top, key=lambda x: (-float(x[5]), x[0]))

def top_n_by_cpa(metrics, n=10):
    """Return top N campaigns with lowest CPA (ascending). Excludes campaigns
    with zero conversions.
    """
    filtered = [m for m in metrics if m[6] is not None]
    if not filtered:
        return []
    if len(filtered) <= n:
        return sorted(filtered, key=lambda x: (float(x[6]), x[0]))[:n]
    top = heapq.nsmallest(n, filtered, key=lambda x: float(x[6]))
    return sorted(top, key=lambda x: (float(x[6]), x[0]))

def stream_csv_rows(file_path):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            yield row

def main():
    parser = argparse.ArgumentParser(description='Ad Performance Aggregator')
    parser.add_argument('--input', '-i', required=True, help='Path to ad_data.csv')
    parser.add_argument('--output', '-o', default='outputs', help='Output directory')
    parser.add_argument('--top', type=int, default=10, help='Top N items to output (default 10)')
    parser.add_argument('--profile', action='store_true', help='Run a simple timing report for phases')
    args = parser.parse_args()

    input_path = args.input
    out_dir = args.output
    top_n = args.top
    do_profile = args.profile

    os.makedirs(out_dir, exist_ok=True)

    print(f"Aggregating file: {input_path}")

    # Phase timing
    t_start = perf_counter()
    rows = stream_csv_rows(input_path)

    t_agg_start = perf_counter()
    agg = aggregate_from_csv_rows(rows)
    t_agg_end = perf_counter()
    print(f"Found {len(agg)} unique campaigns")

    t_metrics_start = perf_counter()
    metrics = compute_metrics(agg)
    t_metrics_end = perf_counter()

    # Top CTR
    t_top_start = perf_counter()
    top_ctr = top_n_by_ctr(metrics, n=top_n)
    top_ctr_rows = [format_row(item) for item in top_ctr]
    top_ctr_path = os.path.join(out_dir, 'top10_ctr.csv')
    write_csv(top_ctr_path, top_ctr_rows)
    t_top_end = perf_counter()
    print(f"Wrote top CTR -> {top_ctr_path}")

    # Top CPA (lowest) exclude zero-conversions
    t_cpa_start = perf_counter()
    top_cpa = top_n_by_cpa(metrics, n=top_n)
    top_cpa_rows = [format_row(item) for item in top_cpa]
    top_cpa_path = os.path.join(out_dir, 'top10_cpa.csv')
    write_csv(top_cpa_path, top_cpa_rows)
    t_cpa_end = perf_counter()
    print(f"Wrote top CPA -> {top_cpa_path}")

    t_end = perf_counter()

    if do_profile:
        total = t_end - t_start
        print("Timings (seconds):")
        print(f"  aggregate: {t_agg_end - t_agg_start:.4f}")
        print(f"  compute_metrics: {t_metrics_end - t_metrics_start:.4f}")
        print(f"  top_ctr + write: {t_top_end - t_top_start:.4f}")
        print(f"  top_cpa + write: {t_cpa_end - t_cpa_start:.4f}")
        print(f"  total: {total:.4f}")



if __name__ == '__main__':
    main()
