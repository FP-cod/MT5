import unittest
from portfolio.position_sizing import size_from_risk

class TestSizing(unittest.TestCase):
    def test_size_from_risk(self):
        units = size_from_risk("AAPL", 100000, 10000, 150)
        self.assertTrue(units >= 0)

if __name__ == '__main__':
    unittest.main()
