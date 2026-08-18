import unittest

from execution.mt5_client import MT5Client


class TestMetaTrader5DryRun(unittest.TestCase):
    def test_mt5_client_connects_in_dry_run(self):
        client = MT5Client(dry_run=True)
        self.assertTrue(client.connect())
        self.assertEqual(client.send_order({"symbol": "EURUSD"}), {"retcode": 10009, "comment": "dry_run"})
        self.assertEqual(client.get_positions(), [])
        client.disconnect()
        self.assertFalse(client.connected)


if __name__ == "__main__":
    unittest.main()
