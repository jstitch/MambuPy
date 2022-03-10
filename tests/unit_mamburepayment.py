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
from MambuPy.rest import mamburepayment

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


class MambuRepaymentTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getrepaymentsurl

        self.assertEqual(mamburepayment.mod_urlfunc, getrepaymentsurl)

    def test_class(self):
        rep = mamburepayment.MambuRepayment(urlfunc=None)
        self.assertTrue(mamburepayment.MambuStruct in rep.__class__.__bases__)

    def test___init__(self):
        rep = mamburepayment.MambuRepayment(urlfunc=None, entid="anything")
        self.assertEqual(rep.entid, "anything")

    def test___repr__(self):
        from datetime import date

        from MambuPy.mambuutil import getrepaymentsurl

        def build_mock_rep_1(self, *args, **kwargs):
            self.attrs = {
                "id": args[1],
                "dueDate": date.today(),
            }

        with mock.patch.object(mamburepayment.MambuStruct, "__init__", build_mock_rep_1):
            rep = mamburepayment.MambuRepayment(
                urlfunc=getrepaymentsurl, entid="mockrepayment"
            )
            self.assertRegexpMatches(
                repr(rep),
                r"^MambuRepayment - duedate: {}".format(
                    date.today().strftime("%Y-%m-%d")
                ),
            )


class MambuRepaymentsTests(unittest.TestCase):
    def test_class(self):
        reps = mamburepayment.MambuRepayments(urlfunc=None)
        self.assertTrue(mamburepayment.MambuStruct in reps.__class__.__bases__)

    def test_iterator(self):
        reps = mamburepayment.MambuRepayments(urlfunc=None)
        reps.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(reps), 3)
        for n, r in enumerate(reps):
            self.assertEqual(str(n), [k for k in r][0])
            self.assertEqual(n, r[str(n)])

    def test_convertDict2Attrs(self):
        from MambuPy.mambuutil import getrepaymentsurl

        reps = mamburepayment.MambuRepayments(urlfunc=None)
        reps.attrs = [
            {"id": "1", "dueDate": "1979-10-23"},
            {"id": "2", "dueDate": "1981-06-08"},
        ]
        with self.assertRaisesRegexp(
            AttributeError,
            "'MambuRepayments' object has no attribute 'mamburepaymentclass'",
        ):
            reps.mamburepaymentclass
        reps.convertDict2Attrs()
        self.assertEqual(
            str(reps.mamburepaymentclass),
            "<class 'MambuPy.rest.mamburepayment.MambuRepayment'>",
        )
        for r in reps:
            self.assertEqual(r.__class__.__name__, "MambuRepayment")
            self.assertEqual(r._MambuStruct__urlfunc, getrepaymentsurl)


if __name__ == "__main__":
    unittest.main()
