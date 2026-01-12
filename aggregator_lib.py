# aggregator_lib.py
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        # strip commas
        v = value.strip().replace(',', '')
        return float(v)
    except (ValueError, AttributeError):
        return default


@dataclass
class CampaignStats:
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    conversions: int = 0

    def update(self, impressions: int, clicks: int, spend: float, conversions: int) -> None:
        self.impressions += impressions
        self.clicks += clicks
        # float accumulation for speed
        self.spend += spend
        self.conversions += conversions

    def ctr(self) -> Optional[float]:
        if self.impressions == 0:
            return None
        return self.clicks / self.impressions

    def cpa(self) -> Optional[float]:
        if self.conversions == 0:
            return None
        return self.spend / self.conversions


def aggregate_from_csv_rows(rows) -> Dict[str, CampaignStats]:
    """
    rows: an iterable of lists/tuples representing csv rows:
      [campaign_id, date, impressions, clicks, spend, conversions]
    Returns dict campaign_id -> CampaignStats (float-based).
    """
    agg: Dict[str, CampaignStats] = {}
    for row in rows:
        if not row or len(row) < 6:
            # skip malformed rows
            continue
        campaign_id = row[0].strip()
        if campaign_id == '' or campaign_id.lower() == 'campaign_id':
            # skip header or empty id
            continue
        impressions = parse_int(row[2], 0)
        clicks = parse_int(row[3], 0)
        spend = parse_float(row[4], 0.0)
        conversions = parse_int(row[5], 0)
        if campaign_id not in agg:
            agg[campaign_id] = CampaignStats()
        agg[campaign_id].update(impressions, clicks, spend, conversions)
    return agg

def compute_metrics(agg: Dict[str, CampaignStats]):
    """
    Returns a list of tuples:
    (campaign_id, impressions, clicks, spend, conversions, ctr, cpa)
    Works with both Decimal-based and float-based CampaignStats.
    """
    out = []
    for cid, stats in agg.items():
        out.append((
            cid,
            stats.impressions,
            stats.clicks,
            stats.spend,
            stats.conversions,
            stats.ctr(),
            stats.cpa()
        ))
    return out
