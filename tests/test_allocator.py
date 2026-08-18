import unittest
from portfolio.allocator import AllocationManager

class TestAllocator(unittest.TestCase):
    def test_normalization_and_expansion(self):
        alloc = AllocationManager("allocations.yaml")
        bw = alloc.get_normalized_bucket_weights()
        self.assertAlmostEqual(sum(bw.values()), 1.0, places=6)
        targets = alloc.expand_to_symbols(100000, {})
        # basic sanity: keys exist
        self.assertTrue(len(targets) > 0)

if __name__ == '__main__':
    unittest.main()
