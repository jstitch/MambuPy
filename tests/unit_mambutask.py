# coding: utf-8

import json
import os
import sys

import requests

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambutask

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text

    def raise_for_status(self):
        return


class MambuTaskTests(unittest.TestCase):
    var_response = '{"task":{"encodedKey":"",\
"id":50221,\
"creationDate":"2024-03-05T00:00:00",\
"lastModifiedDate":"2024-03-05T00:00:00",\
"dueDate":"2024-03-06T00:00:00",\
"title":"MY_TASK",\
"description":"This is a task",\
"createdByUserKey":"",\
"status":"OPEN",\
"taskLinkKey":"",\
"taskLinkType":"GROUP",\
"daysUntilDue":0,\
"assignedUserKey":""}}'

    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import gettasksurl

        self.assertEqual(mambutask.mod_urlfunc, gettasksurl)

    def test_class(self):
        t = mambutask.MambuTask(urlfunc=None)
        self.assertTrue(mambutask.MambuStruct in t.__class__.__bases__)

    def test___init__(self):
        t = mambutask.MambuTask(urlfunc=None, entid="anything")
        self.assertEqual(t.entid, "anything")

    def test___repr__(self):
        from datetime import date

        from MambuPy.mambugeturl import gettasksurl

        def build_mock_task_1(self, *args, **kwargs):
            self.attrs = {"task": {"id": args[1]}}

        def build_mock_task_2(self, *args, **kwargs):
            self.attrs = {
                "task": {
                    "id": args[1],
                    "dueDate": kwargs["data"]["task"]["dueDate"],
                    "status": kwargs["data"]["task"]["status"],
                }
            }

        def build_mock_task_3(self, *args, **kwargs):
            self.attrs = {"id": args[1]}

        def build_mock_task_4(self, *args, **kwargs):
            self.attrs = {
                "id": args[1],
                "dueDate": kwargs["data"]["task"]["dueDate"],
                "status": kwargs["data"]["task"]["status"],
            }

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_1):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="1")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '1'")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_2):
            t = mambutask.MambuTask(
                urlfunc=gettasksurl,
                data={
                    "task": {
                        "dueDate": date.today().strftime("%Y-%m-%d"),
                        "status": "OPEN",
                    }
                },
            )
            self.assertRegexpMatches(
                repr(t), r"^MambuTask - taskid: '', \d+-\d+-\d+, OPEN"
            )

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_3):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="3")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '3'")

        with mock.patch.object(mambutask.MambuStruct, "__init__", build_mock_task_4):
            t = mambutask.MambuTask(
                urlfunc=gettasksurl,
                data={
                    "task": {
                        "dueDate": date.today().strftime("%Y-%m-%d"),
                        "status": "OPEN",
                    }
                },
            )
            self.assertRegexpMatches(
                repr(t), r"^MambuTask - taskid: '', \d+-\d+-\d+, OPEN"
            )

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_create(self, mock_requests):
        mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.exceptions.RetryError = requests.exceptions.RetryError
        # set data response
        mock_requests.Session().post.return_value = Response(self.var_response)
        t = mambutask.MambuTask(connect=False)
        # since we mock requests.post, send any data
        self.assertEqual(t.create({"task": "data"}), 1)
        # at the end of MambuStruct.connect() are stablished all fields with the init() method
        self.assertEqual(t["title"], "MY_TASK")
        self.assertEqual(t["description"], "This is a task")

    def test_close(self):
        from datetime import date

        from MambuPy.mambugeturl import gettasksurl

        def connect_mocked(task):
            task.attrs["task"] = task.attrs
            task.attrs["status"] = "COMPLETED"
            task.attrs["completionDate"] = date.today()

        def build_mock_task(self, *args, **kwargs):
            self.attrs = {
                "id": args[1],
                "encodedKey": "",
                "status": "OPEN",
                "dueDate": date.today(),
                "taskLinkType": "",
                "taskLinkKey": "",
                "title": "",
                "description": "",
                "assignedUserKey": "",
            }

        with mock.patch.object(
            mambutask.MambuStruct, "__init__", build_mock_task
        ), mock.patch.object(mambutask.MambuStruct, "connect", connect_mocked):
            t = mambutask.MambuTask(urlfunc=gettasksurl, entid="1")
            self.assertRegexpMatches(repr(t), r"^MambuTask - taskid: '1'")
            t.close()
            self.assertEqual(t.attrs["status"], "COMPLETED")
            self.assertEqual(
                t.attrs["completionDate"].strftime("%Y-%m-%d"),
                date.today().strftime("%Y-%m-%d"),
            )


class MambuTasksTests(unittest.TestCase):
    def test_class(self):
        ts = mambutask.MambuTasks(urlfunc=None)
        self.assertTrue(mambutask.MambuStruct in ts.__class__.__bases__)

    def test_iterator(self):
        ts = mambutask.MambuTasks(urlfunc=None)
        ts.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(ts), 3)
        for n, a in enumerate(ts):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import gettasksurl

        ts = mambutask.MambuTasks(urlfunc=None)
        ts.attrs = [
            {"id": "my_id", "title": "my_title"},
            {"id": "my_2_id", "title": "my_another_title"},
        ]
        with self.assertRaisesRegex(
            AttributeError, "'MambuTasks' object has no attribute 'mambutaskclass'"
        ):
            ts.mambutaskclass
        ts.convert_dict_to_attrs()
        self.assertEqual(
            str(ts.mambutaskclass), "<class 'MambuPy.rest.mambutask.MambuTask'>"
        )
        for t in ts:
            self.assertEqual(t.__class__.__name__, "MambuTask")
            self.assertEqual(t._MambuStruct__urlfunc, gettasksurl)


if __name__ == "__main__":
    unittest.main()
