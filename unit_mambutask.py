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
                    'dueDate' : kwargs['data']['task']['dueDate'],
                    'status' : kwargs['data']['task']['status'],
                    }
                }
        def build_mock_task_3(self, *args, **kwargs):
            self.attrs = {
                'id' : args[1]
                }
        def build_mock_task_4(self, *args, **kwargs):
            self.attrs = {
                'id' : args[1],
                'dueDate' : kwargs['data']['task']['dueDate'],
                'status' : kwargs['data']['task']['status'],
                }

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_1):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="1")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '1'")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_2):
            t = mambutask.MambuTask(urlfunc=gettasksurl, data={"task":{'dueDate':date.today().strftime("%Y-%m-%d"), 'status':"OPEN"}})
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '', \d+-\d+-\d+, OPEN")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_3):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="3")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '3'")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_4):
            t = mambutask.MambuTask(urlfunc=gettasksurl, data={"task":{'dueDate':date.today().strftime("%Y-%m-%d"), 'status':"OPEN"}})
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '', \d+-\d+-\d+, OPEN")

    def test_close(self):
        from datetime import date
        from mambuutil import gettasksurl
        def connect_mocked(task):
            task.attrs['status']         = "COMPLETED"
            task.attrs['completionDate'] = date.today()
        def build_mock_task(self, *args, **kwargs):
            self.attrs = {
                'id'              : args[1],
                'encodedKey'      : "",
                'status'          : "OPEN",
                'dueDate'         : date.today(),
                'taskLinkType'    : "",
                'taskLinkKey'     : "",
                'title'           : "",
                'description'     : "",
                'assignedUserKey' : "",
                }
        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task) as mock_init, mock.patch.object(mambutask.MambuStruct, "connect", connect_mocked) as mock_connect:
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="1")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '1'")
            t.close()
            self.assertEqual(t.attrs['status'], "COMPLETED")
            self.assertEqual(t.attrs['completionDate'], date.today())


class MambuTasksTests(unittest.TestCase):
    def test_class(self):
        ts = mambutask.MambuTasks(urlfunc=None)
        self.assertTrue(mambutask.MambuStruct in ts.__class__.__bases__)

    def test_iterator(self):
        ts = mambutask.MambuTasks(urlfunc=None)
        ts.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(ts), 3)
        for n,a in enumerate(ts):
            self.assertEqual(str(n), a.keys()[0])
            self.assertEqual(n, a[str(n)])

    def test_convertDict2Attrs(self):
        ts = mambutask.MambuTasks(urlfunc=None)
        ts.attrs = [
            {'id':"my_id", 'title':"my_title"},
            {'id':"my_2_id", 'title':"my_another_title"},
            ]
        ts.convertDict2Attrs()
        for t in ts:
            self.assertEqual(t.__class__.__name__, 'MambuTask')


if __name__ == '__main__':
    unittest.main()
