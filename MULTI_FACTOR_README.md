# Multi-factor allocator

This branch adds a modular multi-factor allocation framework.

Key points:
- Buckets: indices (trend following), crypto (momentum), large_caps (pairs trading), forex (dedicated algo), cash
- Allocations live in allocations.yaml and are normalized by default
- Engine skeleton wires allocator -> risk -> order router -> MT5 client (dry-run by default)
- Backtest skeleton included

Run tests:

pip install -r requirements.txt
python -m unittest discover -v

Note: this is a structural PR with skeletons. The strategies are placeholders and must be connected
with real market data (see data/market_data.py) and instrument-specific order sizing (lot/tick sizes).
