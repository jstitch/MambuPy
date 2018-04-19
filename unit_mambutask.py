# coding: utf-8

import mock
import unittest

import mambutask

class MambuTaskTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from mambuutil import gettasksurl
        self.assertEqual(mambutask.mod_urlfunc, gettasksurl)

    def test_class(self):
        t = mambutask.MambuTask(urlfunc=None)
        self.assertTrue(mambutask.MambuStruct in t.__class__.__bases__)

    def test___init__(self):
        t = mambutask.MambuTask(urlfunc=None, entid="anything")
        self.assertEqual(t.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from mambuutil import gettasksurl
        def build_mock_task_1(self, *args, **kwargs):
            self.attrs = {
                "task" : {
                    'id' : args[1]
                    }
                }
        def build_mock_task_2(self, *args, **kwargs):
            self.attrs = {
                "task" : {
                    'id' : args[1],
                    'title' : kwargs['data']['task']['title'],
                    'dueDate' : kwargs['data']['task']['dueDate'],
                    'status' : kwargs['data']['task']['status'],
                    }
                }

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_1):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="1")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '1'")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_2):
            t = mambutask.MambuTask(urlfunc=gettasksurl, data={"task":{'title':'title', 'dueDate':date.today().strftime("%Y-%m-%d"), 'status':"OPEN"}})
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '', 'title', \d+-\d+-\d+, OPEN")


if __name__ == '__main__':
    unittest.main()
