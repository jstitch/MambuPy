"""Connectors to Mambu.

Currently supports REST and ORM.
"""
from abc import ABC, abstractmethod
import base64
import json
import re

import requests

from ..mambuutil import (
    apipwd, apiuser, apiurl,
    MambuPyError, MambuError,
    PAGINATIONDETAILS,
    DETAILSLEVEL,
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
    def mambu_get(self, entid, prefix):
        """get, a single entity, identified by its entid.

        Args:
          entid (str) - ID for the entity
          prefix (str) - entity's URL prefix
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

class MambuConnectorREST(MambuConnector, MambuConnectorReader):
    """"""

    _tenant = apiurl
    _headers = {
        "Accept": "application/vnd.mambu.v2+json",
        "Authorization": "Basic {}".format(
            base64.b64encode(bytes("{}:{}".format(
                apiuser, apipwd), "utf-8")).decode())}

    def __request(self, method, url, params={}):
        """ requests an url.

        Args:
          method (str)
          url (str)
          params (dict)

        Returns:
          response content (json)

        Raises:
          MambuError in case of 400 or 500 response codes
        """
        resp = requests.request(
            method, url, params=params, headers=self._headers)

        if resp.status_code >= 400:
            content = json.loads(resp.content.decode())
            raise MambuError(
                "{} - {}{}".format(
                    content["errors"][0]["errorCode"],
                    content["errors"][0]["errorReason"],
                    " ("+content["errors"][0]["errorSource"]+")"
                    if "errorSource" in content["errors"][0]
                    else ""
                    ))

        return resp.content

    def mambu_get(self, entid, url_prefix):
        """get, a single entity, identified by its entid.

        Args:
          entid (str) - ID for the entity
          prefix (str) - entity's URL prefix

        Returns:
          response content (str json {})
        """
        url = "https://{}/api/{}/{}".format(
            self._tenant, url_prefix, entid)

        return self.__request("GET", url)

    def mambu_get_all(
        self,
        url_prefix,
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
        params = {}

        if offset != None:
            if type(offset) != int:
                raise MambuPyError("offset must be integer")
            params["offset"] = offset

        if limit != None:
            if type(limit) != int:
                raise MambuPyError("limit must be integer")
            params["limit"] = limit

        if paginationDetails not in PAGINATIONDETAILS:
            raise MambuPyError(
                "paginationDetails must be in {}".format(
                    PAGINATIONDETAILS))
        params["paginationDetails"] = paginationDetails

        if detailsLevel not in DETAILSLEVEL:
            raise MambuPyError(
                "detailsLevel must be in {}".format(
                    DETAILSLEVEL))
        params["detailsLevel"] = detailsLevel

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
            self._tenant, url_prefix)

        return self.__request("GET", url, params=params)
