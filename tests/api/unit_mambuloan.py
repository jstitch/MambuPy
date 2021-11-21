import unittest
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambuloan


class MambuLoan(unittest.TestCase):
    def test_has_prefix(self):
        ml = mambuloan.MambuLoan()
        self.assertEqual(ml._prefix, "loans")


if __name__ == "__main__":
    unittest.main()
