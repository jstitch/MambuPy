"""Connectors to Mambu.

Currently supports REST.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""
import base64
import copy
import json
import mimetypes
import os
import re
import time
import uuid
from abc import ABC, abstractmethod

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ..mambuutil import (ALLOWED_UPLOAD_MIMETYPES, DETAILSLEVEL,
                         MAX_UPLOAD_SIZE, PAGINATIONDETAILS, SEARCH_OPERATORS,
                         UPLOAD_FILENAME_INVALID_CHARS, MambuCommError,
                         MambuError, MambuPyError, apipwd, apiurl, apiuser)


class MambuConnector(ABC):
    """Interface for Connectors"""


class MambuConnectorReader(ABC):
    """Interface for Readers.

    A Reader supports the followint operations:

    - get (gets a single entity)
    - get_all (gets several entities, filtering allowed)
    - search (gets several entities, advanced filtering)
    - get_documents_metadata (gets the metadata of documents attached to some
                              entity)
    """

    @abstractmethod
    def mambu_get(self, entid, prefix, detailsLevel="BASIC"):
        """get, a single entity, identified by its entid.

        Args:
          entid (str): ID for the entity
          prefix (str): entity's URL prefix
          detailsLevel (str BASIC/FULL): ask for extra details or not
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_all(
        self,
        prefix,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None,
        **kwargs
    ):
        """get_all, several entities, filtering allowed

        Args:
          prefix (str): entity's URL prefix
          filters (dict): key-value filters (depends on each entity)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results
          kwargs (dict): extra parameters that a specific entity may receive in
                         its get_all method
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_search(
        self,
        prefix,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
    ):
        """search, several entities, filtering criteria allowed

        Args:
          filterCriteria (list of dicts): fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict): fields according to
                            LoanAccountSortingCriteria
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_documents_metadata(
        self, entid, owner_type,
        offset=None, limit=None, paginationDetails="OFF",
    ):
        """Gets metadata for all the documents attached to an entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          owner_type (str): the type of the owner of the document
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
        """
        raise NotImplementedError

    def mambu_loanaccount_getSchedule(self, loanid):
        """Retrieves the installments schedule

        Args:
          loanid (str): the id or encoded key of the loan account
        """
        raise NotImplementedError


class MambuConnectorWriter(ABC):
    """Interface for Writers.

    A Reader supports the followint operations:

    - update (updates an entity)
    - create (creates an entity)
    - patch (patches an entity)
    - upload_document (gets a single entity)
    - delete_document (gets several entities, filtering allowed)
    """

    @abstractmethod
    def mambu_update(self, entid, prefix, attrs):
        """updates a mambu entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          prefix (str): entity's URL prefix
          attrs (dict): entity to be updated, complying with Mambu's schemas
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_create(self, prefix, attrs):
        """creates a mambu entity

        Args:
          prefix (str): entity's URL prefix
          attrs (dict): entity to be created, complying with Mambu's schemas
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_patch(self, entid, prefix, fields):
        """patches certain parts of a mambu entity"""
        raise NotImplementedError

    @abstractmethod
    def mambu_upload_document(self, owner_type, entid, filename, name, notes):
        """uploads an attachment to this entity

        Args:
          owner_type (str): the type of the owner of the document
          entid (str): the id or encoded key of the entity owning the document
          filename (str): path and filename of file to upload as attachment
          name (str): name to assign to the attached file in Mambu
          notes (str): notes to associate to the attached file in Mambu
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_delete_document(self, documentId):
        """deletes an attachment by its documentId

        Args:
          documentId (str): the id or encodedkey of the document to be deleted
        """
        raise NotImplementedError


class MambuConnectorREST(MambuConnector, MambuConnectorReader, MambuConnectorWriter):
    """A connector for Mambu REST API"""

    _RETRIES = 5
    _tenant = apiurl
    _headers = {
        "Accept": "application/vnd.mambu.v2+json",
        "Authorization": "Basic {}".format(
            base64.b64encode(bytes("{}:{}".format(apiuser, apipwd), "utf-8")).decode()
        ),
    }

    def __request(self, method, url, params=None, data=None, content_type=None):
        """requests an url.

        Args:
          method (str): HTTP method for the request
          url (str): URL for the request
          params (dict): query parameters
          data (serializable list of dicts or dict alone): request body
          content_type (str): an alternative Content-Type to send in headers

        Returns:
          response content (json)

        Raises:
          `MambuError`: in case of 400 or 500 response codes
        """
        if not params:
            params = {}

        headers = copy.copy(self._headers)

        if method in ["POST", "PATCH", "PUT"]:
            headers["Content-Type"] = "application/json"
            headers["Idempotency-Key"] = str(uuid.uuid4())
        if content_type:
            headers["Content-Type"] = content_type

        if data is not None:
            try:
                data = json.dumps(data)
            except TypeError:
                data = data

        self.retries = 0
        while self.retries <= self._RETRIES:
            time.sleep(self.retries)
            try:
                resp = requests.request(
                    method, url, params=params, data=data, headers=headers
                )
            except requests.exceptions.RequestException as req_ex:
                # possible comm error with Mambu, retrying...
                if self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                raise MambuCommError("Comm error with Mambu: {}".format(req_ex))
            except Exception as ex:
                # unknown exception
                if self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                raise MambuCommError("Unknown error with Mambu: {}".format(ex))

            if resp.status_code >= 400:
                # 500 errors retry. 400 errors raise exception immediatly
                if resp.status_code >= 500 and self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                try:
                    content = json.loads(resp.content.decode())
                except ValueError:
                    # in case resp.content doesn't conforms to json
                    content = {
                        "errors": [
                            {
                                "errorCode": "UNKNOWN",
                                "errorReason": resp.content.decode(),
                            },
                        ]
                    }
                raise MambuError(
                    "{} ({}) - {}{}".format(
                        content["errors"][0]["errorCode"],
                        resp.status_code,
                        content["errors"][0]["errorReason"],
                        " (" + content["errors"][0]["errorSource"] + ")"
                        if "errorSource" in content["errors"][0]
                        else "",
                    )
                )
            # succesful request done!
            break  # pragma: no cover
        else:  # pragma: no cover
            # reached _RETRIES limit with no successful request
            raise MambuCommError("COMM Error: I cannot communicate with Mambu")

        return resp.content

    def __validate_query_params(self, **kwargs):
        """Validate query params

        Args:
          **kwargs (dict): query params

        Returns:
          params (dict): validated params for a query
        """
        params = {}

        if "offset" in kwargs and kwargs["offset"] is not None:
            if not isinstance(kwargs["offset"], int):
                raise MambuPyError("offset must be integer")
            params["offset"] = kwargs["offset"]

        if "limit" in kwargs and kwargs["limit"] is not None:
            if not isinstance(kwargs["limit"], int):
                raise MambuPyError("limit must be integer")
            params["limit"] = kwargs["limit"]

        if "paginationDetails" in kwargs:
            if kwargs["paginationDetails"] not in PAGINATIONDETAILS:
                raise MambuPyError(
                    "paginationDetails must be in {}".format(PAGINATIONDETAILS)
                )
            params["paginationDetails"] = kwargs["paginationDetails"]

        if "detailsLevel" in kwargs:
            if kwargs["detailsLevel"] not in DETAILSLEVEL:
                raise MambuPyError("detailsLevel must be in {}".format(DETAILSLEVEL))
            params["detailsLevel"] = kwargs["detailsLevel"]

        return params

    def mambu_get(self, entid, prefix, detailsLevel="BASIC"):
        """get, a single entity, identified by its entid.

        Args:
          entid (str): ID for the entity
          prefix (str): entity's URL prefix
          detailsLevel (str BASIC/FULL): ask for extra details or not

        Returns:
          response content (str json {})
        """
        params = self.__validate_query_params(detailsLevel=detailsLevel)

        url = "https://{}/api/{}/{}".format(self._tenant, prefix, entid)

        return self.__request("GET", url, params=params)

    def mambu_get_all(
        self,
        prefix,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None,
        **kwargs
    ):
        """get_all, several entities, filtering allowed

        Args:
          prefix (str): entity's URL prefix
          filters (dict): key-value filters (depends on each entity)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results
          kwargs (dict): extra parameters that a specific entity may receive in
                         its get_all method

        Returns:
          response content (str json [])
        """
        params = self.__validate_query_params(
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
            detailsLevel=detailsLevel,
        )
        if kwargs:
            params.update(kwargs)

        if sortBy:
            if not isinstance(sortBy, str) or not re.search(
                r"^(\w+:(ASC|DESC),)*(\w+:(ASC|DESC))$", sortBy
            ):
                raise MambuPyError(
                    "sortBy must be a string with format 'field1:ASC,field2:DESC'"
                )
            params["sortBy"] = sortBy

        if filters:
            if not isinstance(filters, dict):
                raise MambuPyError("filters must be a dictionary")
            params.update(filters)

        url = "https://{}/api/{}".format(self._tenant, prefix)

        return self.__request("GET", url, params=params)

    def mambu_search(
        self,
        prefix,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
    ):
        """search, several entities, filtering criteria allowed

        Args:
          prefix (str): entity's URL prefix
          filterCriteria (list of dicts): fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict): fields according to
                            LoanAccountSortingCriteria
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not

        Returns:
          response content (str json [])
        """
        params = self.__validate_query_params(
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
            detailsLevel=detailsLevel,
        )

        data = {}

        if filterCriteria is not None:
            if not isinstance(filterCriteria, list):
                raise MambuPyError("filterCriteria must be a list of dictionaries")
            data["filterCriteria"] = []
            for criteria in filterCriteria:
                if not isinstance(criteria, dict):
                    raise MambuPyError("each filterCriteria must be a dictionary")
                if (
                    "field" not in criteria
                    or "operator" not in criteria
                    or criteria["operator"] not in SEARCH_OPERATORS
                ):
                    raise MambuPyError(
                        "a filterCriteria must have a field and an operator, member of {}".format(
                            SEARCH_OPERATORS
                        )
                    )
                data["filterCriteria"].append(criteria)

        if sortingCriteria is not None:
            if not isinstance(sortingCriteria, dict):
                raise MambuPyError("sortingCriteria must be a dictionary")
            if (
                "field" not in sortingCriteria
                or "order" not in sortingCriteria
                or sortingCriteria["order"] not in ["ASC", "DESC"]
            ):
                raise MambuPyError(
                    "sortingCriteria must have a field and an order, member of {}".format(
                        ["ASC", "DESC"]
                    )
                )
            data["sortingCriteria"] = sortingCriteria

        url = "https://{}/api/{}:search".format(self._tenant, prefix)

        return self.__request("POST", url, params=params, data=data)

    def mambu_update(self, entid, prefix, attrs):
        """updates a mambu entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          prefix (str): entity's URL prefix
          attrs (dict): entity to be updated, complying with Mambu's schemas

        Returns:
          response content (str json {})
        """
        url = "https://{}/api/{}/{}".format(self._tenant, prefix, entid)

        return self.__request("PUT", url, data=attrs)

    def mambu_create(self, prefix, attrs):
        """creates a mambu entity

        Args:
          prefix (str): entity's URL prefix
          attrs (dict): entity to be created, complying with Mambu's schemas

        Returns:
          response content (str json {})
        """
        url = "https://{}/api/{}".format(self._tenant, prefix)

        return self.__request("POST", url, data=attrs)

    def mambu_patch(self, entid, prefix, fields_ops=None):
        """patches certain parts of a mambu entity

        https://api.mambu.com/?python#tocspatchoperation

        Supported: add, remove, replace (move not yet supported)

        Args:
          entid (str): the id or encoded key of the entity
          prefix (str): entity's URL prefix
          fields_ops (list of tuples): each tuple has:
            OP (str): operation ("ADD", "REPLACE", "REMOVE")
            PATH (str): json pointer referencing the location in the target entity
            VALUE (obj, opc): the value of the field (not for REMOVE op)
        """
        if not fields_ops:
            fields_ops = []

        url = "https://{}/api/{}/{}".format(self._tenant, prefix, entid)

        # build data from fields_ops param
        patch_data = []
        for field in fields_ops:
            patch_item = {"op": field[0].strip().lower(), "path": field[1].strip()}
            if field[0] != "REMOVE":
                patch_item["value"] = field[2]
            patch_data.append(patch_item)

        if patch_data:
            return self.__request("PATCH", url, data=patch_data)

    def mambu_upload_document(self, owner_type, entid, filename, name, notes):
        """uploads an attachment to this entity

        Args:
          owner_type (str): the type of the owner of the document
          entid (str): the id or encoded key of the entity owning the document
          filename (str): path and filename of file to upload as attachment
          name (str): name to assign to the attached file in Mambu
          notes (str): notes to associate to the attached file in Mambu

        Returns:
          response content (str json {}) metadata of the attached document
        """
        for char in UPLOAD_FILENAME_INVALID_CHARS:
            if char in os.path.basename(filename):
                raise MambuError("{} name not allowed".format(filename))
        if os.path.basename(filename).count(".") != 1:
            raise MambuError("{} invalid name".format(filename))
        if (
            not mimetypes.guess_type(filename)[0]
            or mimetypes.guess_type(filename)[0].split("/")[1].upper()
            not in ALLOWED_UPLOAD_MIMETYPES
        ):
            raise MambuError("{} mimetype not supported".format(filename))
        if os.path.getsize(filename) > MAX_UPLOAD_SIZE:
            raise MambuError("{} exceeds {} bytes".format(filename, MAX_UPLOAD_SIZE))
        data = {
            "ownerType": owner_type,
            "id": entid,
            "name": name,
            "notes": notes,
            "file": (
                os.path.basename(filename),
                open(filename, "rb"),
                mimetypes.guess_type(filename)[0],
            ),
        }

        encoder = MultipartEncoder(fields=data)

        url = "https://{}/api/documents".format(self._tenant)

        return self.__request(
            "POST", url, data=encoder, content_type=encoder.content_type
        )

    def mambu_get_documents_metadata(
        self, entid, owner_type,
        offset=None, limit=None, paginationDetails="OFF",
    ):
        """Gets metadata for all the documents attached to an entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          owner_type (str): the type of the owner of the document
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
        """
        params = self.__validate_query_params(
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
        )

        params.update({"entity": owner_type})
        params.update({"ownerKey": entid})

        url = "https://{}/api/documents/documentsMetadata".format(self._tenant)

        return self.__request("GET", url, params=params)

    def mambu_delete_document(self, documentId):
        """deletes an attachment by its documentId

        Args:
          documentId (str): the id or encodedkey of the document to be deleted
        """
        url = "https://{}/api/documents/{}".format(self._tenant, documentId)

        self.__request("DELETE", url)

    def mambu_loanaccount_getSchedule(self, loanid):
        """Retrieves the installments schedule of a loan account

        Args:
          loanid (str): the id or encoded key of the loan account
        """
        url = "https://{}/api/{}/{}/schedule".format(
            self._tenant, "loans", loanid)

        return self.__request("GET", url)
