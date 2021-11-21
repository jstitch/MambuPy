""""""
from ..mambuutil import apipwd, apiuser, apiurl

from abc import ABC, abstractmethod
import base64

import requests


class MambuConnector(ABC):
    """"""

class MambuConnectorReader(ABC):
    """"""

    @abstractmethod
    def mambu_get(self, entid, url_prefix):
        """"""
        raise NotImplementedError

    @abstractmethod
    def mambu_get_all(self, url_prefix):
        """"""
        raise NotImplementedError

class MambuConnectorREST(MambuConnector, MambuConnectorReader):
    """"""

    _tenant = apiurl
    _headers = {
        "Accept": "application/vnd.mambu.v2+json",
        "Authorization": "Basic {}".format(
            base64.b64encode(bytes("{}:{}".format(
                apiuser, apipwd), "utf-8")).decode())}

    def mambu_get(self, entid, url_prefix):
        """"""
        url = "https://{}/api/{}/{}".format(
            self._tenant, url_prefix, entid)
        resp = requests.request("GET", url, headers=self._headers)

        return resp.content

    def mambu_get_all(self, url_prefix):
        """"""
        url = "https://{}/api/{}".format(
            self._tenant, url_prefix)
        resp = requests.request("GET", url, headers=self._headers)

        return resp.content
