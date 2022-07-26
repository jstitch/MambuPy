import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambucustomfield


class MambuCustomField(unittest.TestCase):
    def test_implements_interfaces(self):
        mcf = mambucustomfield.MambuCustomField()
        self.assertTrue(isinstance(mcf, mambucustomfield.MambuEntity))

    def test_has_properties(self):
        mcf = mambucustomfield.MambuCustomField()
        self.assertEqual(mcf._prefix, "customfields")


if __name__ == "__main__":
    unittest.main()
