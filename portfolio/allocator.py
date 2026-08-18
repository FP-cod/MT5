from typing import Dict
import yaml
from pathlib import Path

class AllocationManager:
    def __init__(self, allocations_path: str | Path):
        self.path = Path(allocations_path)
        self.raw = self._load()

    def _load(self) -> Dict:
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def get_normalized_bucket_weights(self) -> Dict[str, float]:
        targets = self.raw.get("targets", {})
        normalize = self.raw.get("normalize", True)
        if not normalize:
            return targets
        s = sum(targets.values())
        if s == 0:
            return targets
        return {k: v / s for k, v in targets.items()}

    def expand_to_symbols(self, account_capital: float, prices: Dict[str, float]) -> Dict[str, float]:
        """Return target cash per symbol based on bucket weights and per-bucket symbol splits.
        prices: dict symbol->price used for reference (optional for cash targets)
        """
        bucket_weights = self.get_normalized_bucket_weights()
        buckets = self.raw.get("buckets", {})
        targets = {}
        for bucket, bw in bucket_weights.items():
            bucket_cap = bw * account_capital
            symbols = buckets.get(bucket, {})
            if not symbols:
                # if no symbol breakdown, assign bucket_cap to a synthetic bucket key
                targets[bucket] = bucket_cap
                continue
            # normalize symbol splits
            s = sum(symbols.values())
            if s == 0:
                for sym in symbols.keys():
                    targets[sym] = bucket_cap / len(symbols)
            else:
                for sym, w in symbols.items():
                    targets[sym] = bucket_cap * (w / s)
        return targets
