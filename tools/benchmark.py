#!/usr/bin/env python3
"""Local benchmark runner for the Ad Performance Aggregator.

Usage:
    python -m tools.benchmark --input example_inputs/sample.csv --output results/ --top 10

If `--generate` is provided, it first generates a sample CSV (default: `example_inputs/sample.csv`).
Measures wall-clock time and peak memory (uses `psutil` if installed).
Writes a simple `benchmarks/benchmark.log` with timing and memory info.
"""
import argparse
import subprocess
import sys
import time
import os
from pathlib import Path

try:
    import psutil
except Exception:
    psutil = None


def run_and_measure(cmd, cwd=None, env=None):
    start = time.perf_counter()
    proc = None
    peak_mem = None
    if psutil:
        p = subprocess.Popen(cmd, cwd=cwd, env=env)
        proc = psutil.Process(p.pid)
        # poll until done while sampling memory
        mem_samples = []
        while True:
            if p.poll() is not None:
                break
            try:
                mem = proc.memory_info().rss
                mem_samples.append(mem)
            except Exception:
                pass
            time.sleep(0.05)
        end = time.perf_counter()
        # final sample
        try:
            mem_samples.append(proc.memory_info().rss)
        except Exception:
            pass
        peak_mem = max(mem_samples) if mem_samples else None
        ret = p.returncode
    else:
        # psutil not available, run and measure time only
        ret = subprocess.call(cmd, cwd=cwd, env=env)
        end = time.perf_counter()
    return {'returncode': ret, 'elapsed': end - start, 'peak_rss': peak_mem}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', help='Input CSV path')
    p.add_argument('--output', '-o', default='bench_results', help='Output dir for results')
    p.add_argument('--generate', action='store_true', help='Generate sample data first')
    p.add_argument('--campaigns', type=int, default=200, help='Campaigns for generated sample')
    p.add_argument('--days', type=int, default=365, help='Days for generated sample')
    p.add_argument('--seed', type=int, default=0, help='Random seed for generator')
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / 'benchmark.log'

    if args.generate:
        sample = Path('example_inputs/sample.csv')
        print(f"Generating sample: {sample} campaigns={args.campaigns} days={args.days}")
        subprocess.check_call([sys.executable, '-m', 'tools.generate_sample', '--output', str(sample), '--campaigns', str(args.campaigns), '--days', str(args.days), '--seed', str(args.seed)])
        input_path = sample
    else:
        if not args.input:
            print('Either --input or --generate must be provided')
            sys.exit(2)
        input_path = Path(args.input)

    cmd = [sys.executable, 'aggregator.py', '--input', str(input_path), '--output', str(out_dir), '--top', '10']
    print('Running:', ' '.join(cmd))
    res = run_and_measure(cmd)

    with open(log_path, 'w') as f:
        f.write(f"returncode: {res['returncode']}\n")
        f.write(f"elapsed_seconds: {res['elapsed']:.4f}\n")
        if res['peak_rss']:
            f.write(f"peak_rss_bytes: {res['peak_rss']}\n")
        else:
            f.write("peak_rss_bytes: N/A (psutil not installed)\n")
    print('Wrote log ->', log_path)

if __name__ == '__main__':
    main()
