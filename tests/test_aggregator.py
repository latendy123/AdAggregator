# tests/test_aggregator.py
import os
import tempfile
import csv
from aggregator_lib import aggregate_from_csv_rows, compute_metrics
from aggregator import format_row, top_n_by_ctr, top_n_by_cpa

def test_aggregate_and_metrics():
    rows = [
        ['campaign_id','date','impressions','clicks','spend','conversions'],
        ['CMP001','2025-01-01','12000','300','45.50','12'],
        ['CMP002','2025-01-01','8000','120','28.00','4'],
        ['CMP001','2025-01-02','14000','340','48.20','15'],
        ['CMP003','2025-01-01','5000','60','15.00','0'],  # zero conversions
    ]
    agg = aggregate_from_csv_rows(rows)
    assert 'CMP001' in agg and 'CMP002' in agg and 'CMP003' in agg
    metrics = compute_metrics(agg)
    # find CMP001
    m_map = {m[0]: m for m in metrics}
    c1 = m_map['CMP001']
    assert c1[1] == 26000  # impressions
    assert c1[2] == 640    # clicks
    assert c1[4] == 27     # conversions
    assert isinstance(c1[3], float)

def test_ranking_helpers():
    rows = [
        ['campaign_id','date','impressions','clicks','spend','conversions'],
        ['A','2025-01-01','100','10','10.0','1'],  # ctr 0.1, cpa 10
        ['B','2025-01-01','1000','20','20.0','10'], # ctr 0.02, cpa 2
        ['C','2025-01-01','50','5','25.0','5'], # ctr 0.1, cpa 5
    ]
    agg = aggregate_from_csv_rows(rows)
    metrics = compute_metrics(agg)
    top_ctr = top_n_by_ctr(metrics, n=3)
    # CTR ranking: A and C tie at 0.1, but ordering by campaign id desc due to reverse sort tie behavior -> ensure both present
    ctr_ids = set(m[0] for m in top_ctr)
    assert {'A','C','B'} == ctr_ids
    top_cpa = top_n_by_cpa(metrics, n=3)
    # lowest CPA first: B (2.0), C (5.0), A (10.0)
    assert [m[0] for m in top_cpa] == ['B','C','A']
