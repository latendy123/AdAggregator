# tests/test_cli.py
import os
import sys
import tempfile
import csv
from aggregator import main as cli_main


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def read_first_column(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        return [r[0] for r in reader]


def test_cli_produces_expected_outputs(tmp_path, monkeypatch, capsys):
    # Create a small CSV with controlled campaigns
    rows = [
        ['campaign_id','date','impressions','clicks','spend','conversions'],
        ['HIGHCTR','2025-01-01','100','50','10.0','1'],   # CTR 0.5, CPA 10
        ['LOWCPA','2025-01-01','1000','50','100.0','100'], # CTR 0.05, CPA 1
        ['OTHER','2025-01-01','500','5','25.0','2'],      # CTR 0.01, CPA 12.5
    ]
    input_path = tmp_path / 'sample.csv'
    out_dir = tmp_path / 'out'
    write_csv(str(input_path), rows)

    # Call CLI programmatically by monkeypatching argv
    monkeypatch.setattr(sys, 'argv', ['aggregator.py', '--input', str(input_path), '--output', str(out_dir), '--top', '2'])
    cli_main()

    top_ctr = read_first_column(str(out_dir / 'top10_ctr.csv'))
    top_cpa = read_first_column(str(out_dir / 'top10_cpa.csv'))

    assert 'HIGHCTR' in top_ctr
    # Lowest CPA first should be LOWCPA
    assert top_cpa[0] == 'LOWCPA'
