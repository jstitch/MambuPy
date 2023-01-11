import json
import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities


class MambuCommentableEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class_commentable(
            entities.MambuEntity, entities.MambuEntityCommentable
        ):
            _prefix = "un_prefix"
            _ownerType = "MY_ENTITY"
            _connector = mock.Mock()

            def __init__(self, **kwargs):
                super().__init__(connector=self._connector, **kwargs)
                self._attrs = {"id": "12345"}

        self.child_class_commentable = child_class_commentable

    def test_get_comments(self):
        child = self.child_class_commentable()
        mock_connector = child._connector
        mock_connector.mambu_get_comments.return_value = b"""[{
        "encodedKey":"my_comment_EK",
        "ownerKey":"my_owner_Key",
        "ownerType":"MY_ENTITY",
        "creationDate":"2022-07-11T12:33:21-05:00",
        "lastModifiedDate":"2022-07-11T12:33:46-05:00",
        "text":"LITTLE PIGS LITTLE PIGS LET ME IN!",
        "userKey":"author_EK"
        }]"""

        comments = child.get_comments()

        self.assertEqual(len(child._comments), 1)
        self.assertEqual(
            child._comments[0]._attrs,
            {
                "encodedKey": "my_comment_EK",
                "ownerKey": "my_owner_Key",
                "ownerType": "MY_ENTITY",
                "creationDate": "2022-07-11T12:33:21-05:00",
                "lastModifiedDate": "2022-07-11T12:33:46-05:00",
                "text": "LITTLE PIGS LITTLE PIGS LET ME IN!",
                "userKey": "author_EK"
            })

        self.assertEqual(
            comments,
            json.loads(mock_connector.mambu_get_comments.return_value))

        mock_connector.mambu_get_comments.assert_called_once_with(
            owner_id="12345", owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF")

    def test_comment(self):
        child = self.child_class_commentable()
        mock_connector = child._connector

        mock_connector.mambu_comment.return_value = b"""{
        "encodedKey":"my_new_commentEk",
        "ownerKey":"my_owner_Key",
        "ownerType":"MY_ENTITY",
        "creationDate":"2022-07-21T18:22:19-05:00",
        "lastModifiedDate":"2022-07-21T18:22:19-05:00",
        "text":"NOT BY THE HAIR OF MY CHINNY, CHIN, CHIN!",
        "userKey":"author_EK"
        }"""

        child._comments=[entities.MambuComment(**{"text": "original comment"})]
        comnt = child.comment("NOT BY THE HAIR OF MY CHINNY, CHIN, CHIN!")

        self.assertEqual(len(child._comments), 2)
        self.assertEqual(
            child._comments[0]._attrs,
            {
                "encodedKey": "my_new_commentEk",
                "ownerKey": "my_owner_Key",
                "ownerType": "MY_ENTITY",
                "text": "NOT BY THE HAIR OF MY CHINNY, CHIN, CHIN!",
                "creationDate": "2022-07-21T18:22:19-05:00",
                "lastModifiedDate": "2022-07-21T18:22:19-05:00",
                "userKey": "author_EK"
            },
        )
        self.assertEqual(comnt, mock_connector.mambu_comment.return_value)
        mock_connector.mambu_comment.assert_called_with(
            owner_id="12345",
            owner_type="MY_ENTITY",
            text="NOT BY THE HAIR OF MY CHINNY, CHIN, CHIN!",
        )


if __name__ == "__main__":
    unittest.main()
