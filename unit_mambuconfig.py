# coding: utf-8

import mock
import unittest
from datetime import datetime

import mambuconfig


class MambuConfigTests(unittest.TestCase):
    def test_api_attrs(self):
        self.assertEqual(mambuconfig.apiurl, "domain.mambu.com")
        self.assertEqual(mambuconfig.apiuser, "mambu_api_user")
        self.assertEqual(mambuconfig.apipwd, "mambu_api_password")

    def test_db_attrs(self):
        self.assertEqual(mambuconfig.dbname, "mambu_db")
        self.assertEqual(mambuconfig.dbuser, "mambu_db_user")
        self.assertEqual(mambuconfig.dbpwd, "mambu_db_pwd")
        self.assertEqual(mambuconfig.dbhost, "localhost")
        self.assertEqual(mambuconfig.dbport, "3306")
        self.assertEqual(mambuconfig.dbeng, "mysql")


if __name__ == '__main__':
    unittest.main()
