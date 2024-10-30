"""Connectors to Mambu.

Currently supports REST.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import base64
import copy
import json
import logging
import mimetypes
import os
import re
import uuid

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .mambuconnector import MambuConnector, MambuConnectorReader, MambuConnectorWriter
from MambuPy.mambuutil import (
    ALLOWED_UPLOAD_MIMETYPES,
    DETAILSLEVEL,
    MAX_UPLOAD_SIZE,
    PAGINATIONDETAILS,
    SEARCH_OPERATORS,
    OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
    UPLOAD_FILENAME_INVALID_CHARS,
    MambuCommError,
    MambuError,
    MambuPyError,
    apipwd,
    apiurl,
    apiuser,
)


logger = logging.getLogger(__name__)
logger.propagate = True


class MambuConnectorREST(MambuConnector, MambuConnectorReader, MambuConnectorWriter):
    """A connector for Mambu REST API"""

    _RETRIES = 5
    _tenant = ""
    _headers = {}

    def __init__(self, user=apiuser, pwd=apipwd, url=apiurl, **kwargs):
        self._headers = {
            "Accept": "application/vnd.mambu.v2+json",
            "Authorization": "Basic {}".format(
                base64.b64encode(bytes("{}:{}".format(user, pwd), "utf-8")).decode()
            ),
        }
        self._tenant = url

    def __request_headers(self, method, content_type):
        headers = copy.copy(self._headers)

        if method in ["POST", "PATCH", "PUT"]:
            headers["Content-Type"] = "application/json"
            headers["Idempotency-Key"] = str(uuid.uuid4())
        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def __request_params(self, params):
        if not params:
            params = {}
        return params

    def __request_data(self, data):
        if data is not None:
            try:
                data = json.dumps(data)
            except TypeError:
                data = data
        return data

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
        headers = self.__request_headers(method, content_type)
        params = self.__request_params(params)
        data = self.__request_data(data)

        retry_strategy = Retry(
            total=self._RETRIES,
            status_forcelist=[429, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=[
                "HEAD",
                "GET",
                "OPTIONS",
                "POST",
                "PUT",
                "DELETE",
                "TRACE",
                "PATCH",
            ],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        resp = ""
        try:
            logger.debug(
                "about to make %s request: \
url %s, params %s, data %s, headers %s",
                method,
                url,
                [(k, v) for k, v in params.items() if k not in ["pwd"]],
                data,
                [(k, v) for k, v in headers.items() if k != "Authorization"],
            )
            resp = http.request(method, url, params=params, data=data, headers=headers)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httperr:
            logger.error(
                "%s on %s request: params %s, data %s, headers %s",
                str(httperr),
                method,
                params,
                data,
                [(k, v) for k, v in headers.items()],
            )
            if hasattr(resp, "content"):  # pragma: no cover
                logger.error("HTTPError, resp content: %s", resp.content)
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
            try:
                error = content["errors"][0]
            except KeyError:
                error = content
            raise MambuError(
                "{} ({}) - {}{}".format(
                    error["errorCode"] if "errorCode" in error else error["returnCode"],
                    resp.status_code,
                    (
                        error["errorReason"]
                        if "errorReason" in error
                        else error["returnStatus"]
                    ),
                    " (" + error["errorSource"] + ")" if "errorSource" in error else "",
                )
            )
        except requests.exceptions.RetryError as rerr:  # pragma: no cover
            logger.error(
                "%s MambuCommError on %s request: url %s, params %s, data %s, headers %s",
                str(rerr),
                method,
                url,
                params,
                data,
                [(k, v) for k, v in headers.items()],
            )
            raise MambuCommError(
                "COMM Error: I cannot communicate with Mambu: {}".format(rerr)
            )
        except Exception as ex:
            logger.exception(
                "%s Exception (%s) on %s request: url %s, params %s, data %s, headers %s",
                str(ex),
                resp,
                method,
                url,
                params,
                data,
                [(k, v) for k, v in headers.items()],
            )
            if hasattr(resp, "content"):  # pragma: no cover
                logger.error("Exception, resp content: %s", resp.content)
            raise MambuCommError("Unknown comm error with Mambu: {}".format(ex))

        logger.debug("response %s to %s:\n%s", resp, method, resp.content)

        return resp.content

    def __list_request_args(self, params):
        if not params:
            params = {}
        if "limit" in params and params["limit"] is not None:
            ini_limit = params["limit"]
        else:
            ini_limit = 0
        if "offset" in params and params["offset"] is not None:
            offset = params["offset"]
        else:
            offset = 0

        return (params, ini_limit, offset)

    def __list_request_cat_response(self, list_resp, resp):
        if list_resp == b"":
            list_resp = resp
        elif len(json.loads(resp.decode())) > 0:
            list_resp = list_resp[:-1] + b"," + resp[1:]

        return list_resp

    def __list_request(self, method, url, params=None, data=None):
        """Request for a list, appending responses with limit and offset.

        Makes several requests adjusting limits and offsets, appending
        responses, just as if you have made a single request with a
        big response.

        Useful for services where you have a Maximum limit of response
        elements but wish to make a single call as if doing a single
        request (but not, you make as many as necessary until covering
        the given limit).

        Args:
          method (str): HTTP method for the request
          url (str): URL for the request
          params (dict): query parameters
          data (serializable list of dicts or dict alone): request body
        """
        (params, ini_limit, offset) = self.__list_request_args(params)

        window = True
        list_resp = b""
        while window:
            if not ini_limit or ini_limit > OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE:
                limit = OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
            else:
                limit = ini_limit

            params["offset"] = offset
            params["limit"] = limit if limit != 0 else None

            resp = self.__request(
                method, url, params=copy.copy(params), data=copy.copy(data)
            )

            jsonresp = list(json.loads(resp.decode()))
            if len(jsonresp) < limit:
                window = False

            list_resp = self.__list_request_cat_response(list_resp, resp)

            # next window, moving offset...
            offset = offset + limit
            if ini_limit:
                ini_limit -= limit
                if ini_limit <= 0:
                    window = False

        return list_resp

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

    def __validate_filter_criteria(self, filterCriteria):
        """Validate search filter criteria

        Args:
          filterCriteria (list of dicts): filter criteria

        Returns:
          validated_filterCriteria (list of dicts): validated filter criteria

        Raises:
          MambuPyError (obj): when invalid filterCriteria
        """
        validated_filterCriteria = []
        if not isinstance(filterCriteria, list) or any(
            [criteria for criteria in filterCriteria if not isinstance(criteria, dict)]
        ):
            raise MambuPyError("filterCriteria must be a list of dictionaries")
        for criteria in filterCriteria:
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
            validated_filterCriteria.append(criteria)

        return validated_filterCriteria

    def __validate_sorting_criteria(self, sortingCriteria):
        """Validate search sorting criteria

        Args:
          sortingCriteria (dict): sorting criteria

        Returns:
          sortingCriteria (dict): validated sorting criteria

        Raises:
          MambuPyError (obj): when invalid sortingCriteria
        """
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

        return sortingCriteria

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

        return self.__list_request("GET", url, params=params)

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
            data["filterCriteria"] = self.__validate_filter_criteria(filterCriteria)

        if sortingCriteria is not None:
            data["sortingCriteria"] = self.__validate_sorting_criteria(sortingCriteria)

        url = "https://{}/api/{}:search".format(self._tenant, prefix)

        return self.__list_request("POST", url, params=params, data=data)

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

    def mambu_delete(self, entid, prefix):
        """deletes a mambu entity"""
        url = "https://{}/api/{}/{}".format(self._tenant, prefix, entid)

        return self.__request("DELETE", url)

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
        self,
        entid,
        owner_type,
        offset=None,
        limit=None,
        paginationDetails="OFF",
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
        url = "https://{}/api/{}/{}/schedule".format(self._tenant, "loans", loanid)

        return self.__request("GET", url)

    def mambu_loanaccount_writeoff(self, loanid, notes):
        """Writesoff a loan account

        Args:
          loanid (str): the id or encoded key of the loan account
          notes (str): notes to associate to the writeoff operation in Mambu
        """
        url = "https://{}/api/{}/{}:writeOff".format(self._tenant, "loans", loanid)
        data = {"notes": notes}
        return self.__request("POST", url, data=data)

    def mambu_change_state(self, entid, prefix, action, notes):
        """change state of mambu entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          prefix (str): entity's URL prefix
          action (str): specify the action state
          notes (str): notes to associate to the change of status
        """
        url = "https://{}/api/{}/{}:changeState".format(self._tenant, prefix, entid)
        data = {"action": action, "notes": notes}
        return self.__request("POST", url, data=data)

    def mambu_get_customfield(self, customfieldid):
        """Retrieves a Custom Field.

        Args:
          customfieldid (str): the id or encoded key of the custom field
        """
        url = "https://{}/api/customfields/{}".format(self._tenant, customfieldid)
        return self.__request("GET", url)

    def mambu_get_comments(
        self, owner_id, owner_type, offset=None, limit=None, paginationDetails="OFF"
    ):
        """Retrieves the comments of entity with owner_id.

        Args:
          owner_id (str): the id or encoded key of the owner
          owner_type (str): the type of the entity owning the comments
        """
        params = self.__validate_query_params(
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
        )
        if owner_type not in [
            "CLIENT",
            "GROUP",
            "LOAN_PRODUCT",
            "SAVINGS_PRODUCT",
            "CENTRE",
            "BRANCH",
            "USER",
            "LOAN_ACCOUNT",
            "DEPOSIT_ACCOUNT",
            "ID_DOCUMENT",
            "LINE_OF_CREDIT",
            "GL_JOURNAL_ENTRY",
        ]:
            raise MambuError("Owner {} not allowed".format(owner_type))

        params.update({"ownerType": owner_type})
        params.update({"ownerKey": owner_id})

        url = "https://{}/api/comments".format(self._tenant)

        return self.__request("GET", url, params=params)

    def mambu_comment(self, owner_id, owner_type, text):
        """Comments an entity with owner_id.

        Args:
          owner_id (str): the id or encoded key of the owner
          owner_type (str): the type of the entity owning the comments
          text (str): the text of the comment
        """
        if owner_type not in [
            "CLIENT",
            "GROUP",
            "LOAN_PRODUCT",
            "SAVINGS_PRODUCT",
            "CENTRE",
            "BRANCH",
            "USER",
            "LOAN_ACCOUNT",
            "DEPOSIT_ACCOUNT",
            "ID_DOCUMENT",
            "LINE_OF_CREDIT",
            "GL_JOURNAL_ENTRY",
        ]:
            raise MambuError("Owner {} not allowed".format(owner_type))
        data = {"ownerKey": owner_id, "ownerType": owner_type, "text": text}

        url = "https://{}/api/comments".format(self._tenant)

        return self.__request("POST", url, data=data)

    def mambu_make_disbursement(
        self, loan_id, notes, firstRepaymentDate, valueDate, allowed_fields, **kwargs
    ):
        """Make a disbursement transacton on a loan account.

        Args:
          loan_id (str): loan account id  to disburse
          firstRepaymentDate (str): first repayment date in ISO format
          notes (str): notes for the disbursement transaction
          valueDate (str): entrydate for disbursement transaction in ISO format
          allowed_fields (list): extra fields allowed for the transaction
          kwargs (dict): key-values of extra fields for the transaction
        """
        data = {
            "firstRepaymentDate": firstRepaymentDate,
            "notes": notes,
            "valueDate": valueDate,
        }
        for k, v in kwargs.items():
            if k in allowed_fields:
                data[k] = v

        url = "https://{}/api/loans/{}/disbursement-transactions".format(
            self._tenant, loan_id
        )

        return self.__request("POST", url, data=data)

    def mambu_make_repayment(
        self, loan_id, amount, notes, valueDate,
        allowed_fields, loantransaction_allowed_fields,
        **kwargs
    ):
        """Make a repayment transaction on a loan account.

        Args:
          loan_id (str): loan account id to make a repayment
          amount (float): the amount of the repayment
          notes (str): notes for the repayment transaction
          valueDate (str): date for the repayment transaction in ISO format
          allowed_fields (list): extra fields allowed for the transaction
          loantransaction_allowed_fields (list): extra fields allowed for the transaction details
          kwargs (dict): key-values of extra fields for the transaction
                         allows custom fields in the transaction ONLY when prefixed with '_' and being a dict
        """
        def _extract_valid_transactionDetails(transactionDetails_dict):
            transactionDetails = {}
            for k, v in transactionDetails_dict.items():
                if k in loantransaction_allowed_fields:
                    transactionDetails[k] = v
            return transactionDetails

        data = {"amount": amount, "notes": notes, "valueDate": valueDate}
        for k, v in kwargs.items():
            if k in allowed_fields:
                if k == "transactionDetails":
                    data[k] = _extract_valid_transactionDetails(v)
                else:
                    data[k] = v
            elif k[0] == "_" and isinstance(v, dict):
                data[k] = v

        url = "https://{}/api/loans/{}/repayment-transactions".format(
            self._tenant, loan_id
        )

        return self.__request("POST", url, data=data)

    def mambu_make_fee(
        self, loan_id, amount, installmentNumber, notes, valueDate, allowed_fields, **kwargs
    ):
        """Make a fee transaction on a loan account.

        Args:
          loan_id (str): loan account id to apply a fee
          amount (float): the amount of the fee
          installmentNumber (int): the installment number to apply the fee
          notes (str): notes for the fee transaction
          valueDate (str): entry date for the fee transaction
          allowed_fields (list): extra fields allowed for the transaction
          kwargs (dict): key-values of extra fields for the transaction
        """
        data = {
            "amount": amount,
            "installmentNumber": installmentNumber,
            "notes": notes,
            "valueDate": valueDate,
        }
        for k, v in kwargs.items():
            if k in allowed_fields:
                data[k] = v

        url = "https://{}/api/loans/{}/fee-transactions".format(self._tenant, loan_id)

        return self.__request("POST", url, data=data)

    def mambu_loantransaction_adjust(self, transactionid, notes):
        """Adjust a loan transaction

        Args:
          transactionid (str): the id or encoded key of the loan transaction
          notes (str): notes to associate to the transaction adjustment in Mambu
        """
        data = {
            "notes": notes,
        }

        url = "https://{}/api/loans/transactions/{}:adjust".format(self._tenant, transactionid)

        return self.__request("POST", url, data=data)
