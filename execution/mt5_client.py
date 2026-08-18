import MetaTrader5 as mt5

class MT5Client:
    def __init__(self, config: dict | None = None, dry_run: bool = True):
        self.config = config or {}
        self.dry_run = dry_run
        self.connected = False

    def connect(self) -> bool:
        if self.dry_run:
            self.connected = True
            return True
        self.connected = mt5.initialize()
        return self.connected

    def disconnect(self) -> None:
        if not self.dry_run:
            mt5.shutdown()
        self.connected = False

    def send_order(self, order: dict) -> dict:
        """order: dict with fields depending on MT5 API. In dry_run we just log and return fake response."""
        if self.dry_run:
            print("DRY_RUN send_order:", order)
            return {"retcode": 10009, "comment": "dry_run"}
        resp = mt5.order_send(order)
        return resp

    def get_positions(self):
        if self.dry_run:
            return []
        return mt5.positions_get()
