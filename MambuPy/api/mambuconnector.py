"""Connectors to Mambu.

Currently supports REST and ORM.
"""
from abc import ABC, abstractmethod
import base64
import copy
import json
import re
import time
import uuid

from json import JSONDecodeError

import requests

from ..mambuutil import (
    apipwd, apiuser, apiurl,
    MambuPyError, MambuError, MambuCommError,
    PAGINATIONDETAILS,
    DETAILSLEVEL,
    SEARCH_OPERATORS,
    )


class MambuConnector(ABC):
    """ Interface for Connectors"""

class MambuConnectorReader(ABC):
    """ Interface for Readers.

    A Reader supports the followint operations:

    - get (gets a single entity)
    - get_all (gets several entities, filtering allowed)
    - search (gets several entities, advanced filtering)
    """

    @abstractmethod
    def mambu_get(self, entid, prefix, detailsLevel="BASIC"):
        """get, a single entity, identified by its entid.

        Args:
          entid (str) - ID for the entity
          prefix (str) - entity's URL prefix
          detailsLevel (str BASIC/FULL) - ask for extra details or not
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
        sortBy=None
    ):
        """get_all, several entities, filtering allowed

        Args:
          prefix (str) - entity's URL prefix
          filters (dict) - key-value filters (depends on each entity)
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not
          sortBy (str field:ASC,field2:DESC) - sorting criteria for results
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_search(
        self,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC"
    ):
        """search, several entities, filtering criteria allowed

        Args:
          filterCriteria (list of dicts) - fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict) - fields according to
                            LoanAccountSortingCriteria
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not
        """
        raise NotImplementedError

class MambuConnectorREST(MambuConnector, MambuConnectorReader):
    """"""

    _RETRIES = 5
    _tenant = apiurl
    _headers = {
        "Accept": "application/vnd.mambu.v2+json",
        "Authorization": "Basic {}".format(
            base64.b64encode(bytes("{}:{}".format(
                apiuser, apipwd), "utf-8")).decode())}

    def __request(self, method, url, params={}, data=None):
        """ requests an url.

        Args:
          method (str) - HTTP method for the request
          url (str) - URL for the request
          params (dict) - query parameters
          data (serializable list of dicts or dict alone) - request body

        Returns:
          response content (json)

        Raises:
          MambuError in case of 400 or 500 response codes
        """
        headers = copy.copy(self._headers)

        if method in ["POST", "PATCH", "PUT"]:
            headers["Content-Type"] = "application/json"
            headers["Idempotency-Key"] = str(uuid.uuid4())
        if data != None:
            data = json.dumps(data)

        self.retries = 0
        while self.retries <= self._RETRIES:
            time.sleep(self.retries)
            try:
                resp = requests.request(
                    method, url, params=params, data=data, headers=headers)
            except requests.exceptions.RequestException as req_ex:
                """ possible comm error with Mambu, retrying... """
                if self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                else:
                    raise MambuCommError(
                        "Comm error with Mambu: {}".format(req_ex))
            except Exception as ex:
                """ unknown exception """
                if self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                else:
                    raise MambuCommError(
                        "Unknown error with Mambu: {}".format(ex))

            if resp.status_code >= 400:
                """ 500 errors retry. 400 errors raise exception immediatly """
                if resp.status_code >= 500 and self.retries < self._RETRIES:
                    self.retries += 1
                    continue
                else:
                    try:
                        content = json.loads(resp.content.decode())
                    except (JSONDecodeError, ValueError):
                        """ in case resp.content doesn't conforms to json """
                        content = {"errors": [
                            {"errorCode": "UNKNOWN",
                             "errorReason": resp.content.decode(),},
                            ]}
                    raise MambuError(
                        "{} ({}) - {}{}".format(
                            content["errors"][0]["errorCode"],
                            resp.status_code,
                            content["errors"][0]["errorReason"],
                            " ("+content["errors"][0]["errorSource"]+")"
                            if "errorSource" in content["errors"][0]
                            else ""
                            ))
            # succesful request done!
            break  # pragma: no cover
        else:  # pragma: no cover
            """ reached _RETRIES limit with no successful request """
            raise MambuCommError("COMM Error: I cannot communicate with Mambu")

        return resp.content

    def __validate_query_params(self, **kwargs):
        """Validate query params

        Args:
          **kwargs (dict) - query params

        Returns:
          params (dict) - validated params for a query
        """
        params = {}

        if "offset" in kwargs and kwargs["offset"] != None:
            if type(kwargs["offset"]) != int:
                raise MambuPyError("offset must be integer")
            params["offset"] = kwargs["offset"]

        if "limit" in kwargs and kwargs["limit"] != None:
            if type(kwargs["limit"]) != int:
                raise MambuPyError("limit must be integer")
            params["limit"] = kwargs["limit"]

        if "paginationDetails" in kwargs:
            if kwargs["paginationDetails"] not in PAGINATIONDETAILS:
                raise MambuPyError(
                    "paginationDetails must be in {}".format(
                        PAGINATIONDETAILS))
            params["paginationDetails"] = kwargs["paginationDetails"]

        if "detailsLevel" in kwargs:
            if kwargs["detailsLevel"] not in DETAILSLEVEL:
                raise MambuPyError(
                    "detailsLevel must be in {}".format(
                        DETAILSLEVEL))
            params["detailsLevel"] = kwargs["detailsLevel"]

        return params

    def mambu_get(
        self,
        entid,
        prefix,
        detailsLevel="BASIC"
    ):
        """get, a single entity, identified by its entid.

        Args:
          entid (str) - ID for the entity
          prefix (str) - entity's URL prefix
          detailsLevel (str BASIC/FULL) - ask for extra details or not

        Returns:
          response content (str json {})
        """
        params = self.__validate_query_params(detailsLevel=detailsLevel)

        url = "https://{}/api/{}/{}".format(
            self._tenant, prefix, entid)

        return self.__request("GET", url, params=params)

    def mambu_get_all(
        self,
        prefix,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None
    ):
        """get_all, several entities, filtering allowed

        Args:
          prefix (str) - entity's URL prefix
          filters (dict) - key-value filters (depends on each entity)
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not
          sortBy (str field:ASC,field2:DESC) - sorting criteria for results

        Returns:
          response content (str json [])
        """
        params = self.__validate_query_params(
            offset=offset, limit=limit,
            paginationDetails=paginationDetails,
            detailsLevel=detailsLevel)

        if sortBy:
            if (type(sortBy) != str
                or not re.search(
                    r"^(\w+:(ASC|DESC),)*(\w+:(ASC|DESC))$", sortBy)
            ):
                raise MambuPyError(
                    "sortBy must be a string with format 'field1:ASC,field2:DESC'")
            params["sortBy"] = sortBy

        if filters:
            if type(filters) != dict:
                raise MambuPyError("filters must be a dictionary")
            params.update(filters)

        url = "https://{}/api/{}".format(
            self._tenant, prefix)

        return self.__request("GET", url, params=params)

    def mambu_search(
        self,
        prefix,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC"
    ):
        """search, several entities, filtering criteria allowed

        Args:
          prefix (str) - entity's URL prefix
          filterCriteria (list of dicts) - fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict) - fields according to
                            LoanAccountSortingCriteria
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not

        Returns:
          response content (str json [])
        """
        params = self.__validate_query_params(
            offset=offset, limit=limit,
            paginationDetails=paginationDetails,
            detailsLevel=detailsLevel)

        data = {}

        if filterCriteria != None:
            if type(filterCriteria) != list:
                raise MambuPyError("filterCriteria must be a list of dictionaries")
            data["filterCriteria"] = []
            for criteria in filterCriteria:
                if type(criteria) != dict:
                    raise MambuPyError("each filterCriteria must be a dictionary")
                if (
                    "field" not in criteria
                    or "operator" not in criteria
                    or criteria["operator"] not in SEARCH_OPERATORS
                ):
                    raise MambuPyError(
                        "a filterCriteria must have a field and an operator, member of {}".format(
                            SEARCH_OPERATORS))
                data["filterCriteria"].append(criteria)

        if sortingCriteria != None:
            if type(sortingCriteria) != dict:
                raise MambuPyError("sortingCriteria must be a dictionary")
            if (
                "field" not in sortingCriteria
                or "order" not in sortingCriteria
                or sortingCriteria["order"] not in ["ASC", "DESC"]
            ):
                raise MambuPyError(
                    "sortingCriteria must have a field and an order, member of {}".format(
                        ["ASC", "DESC"]))
            data["sortingCriteria"] = sortingCriteria

        url = "https://{}/api/{}:search".format(
            self._tenant, prefix)

        return self.__request("POST", url, params=params, data=data)
