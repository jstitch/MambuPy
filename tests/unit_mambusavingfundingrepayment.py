# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambusavingfundingrepayment

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuActivityTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getsavingfundingrepaymentsurl

        self.assertEqual(mambusavingfundingrepayment.mod_urlfunc, getsavingfundingrepaymentsurl)

    def test_class(self):
        a = mambusavingfundingrepayment.MambuSavingFundingRepayment(urlfunc=None)
        self.assertTrue(mambusavingfundingrepayment.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambusavingfundingrepayment.MambuSavingFundingRepayment(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")

    def test___repr__(self):
        from datetime import date

        from MambuPy.mambugeturl import getsavingfundingrepaymentsurl

        def build_mock_rep_1(self, *args, **kwargs):
            self.attrs = {
                "id": args[1],
                "dueDate": date.today(),
            }

        with mock.patch.object(mambusavingfundingrepayment.MambuStruct, "__init__", build_mock_rep_1):
            rep = mambusavingfundingrepayment.MambuSavingFundingRepayment(
                urlfunc=getsavingfundingrepaymentsurl, entid="mockrepayment"
            )
            self.assertRegexpMatches(
                repr(rep),
                r"^MambuSavingFundingRepayment - duedate: {}".format(
                    date.today().strftime("%Y-%m-%d")
                ),
            )


class MambuRepaymentsTests(unittest.TestCase):
    def test_class(self):
        acs = mambusavingfundingrepayment.MambuSavingFundingRepayments(urlfunc=None)
        self.assertTrue(mambusavingfundingrepayment.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambusavingfundingrepayment.MambuSavingFundingRepayments(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getsavingfundingrepaymentsurl

        acs = mambusavingfundingrepayment.MambuSavingFundingRepayments(urlfunc=None)
        acs.attrs = [
            {"activity": "my_act"},
            {"activity": "my_2_act"},
        ]
        with self.assertRaisesRegex(
            AttributeError,
            "'MambuSavingFundingRepayments' object has no attribute 'repayment'",
        ):
            acs.repayment
        acs.convert_dict_to_attrs()
        """self.assertEqual(
            str(acs.MambuSavingFundingRepayment),
            "<class 'MambuPy.rest.mambuactivity.repayment'>",
        )"""
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuSavingFundingRepayment")
            self.assertEqual(a._MambuStruct__urlfunc, getsavingfundingrepaymentsurl)


if __name__ == "__main__":
    unittest.main()
