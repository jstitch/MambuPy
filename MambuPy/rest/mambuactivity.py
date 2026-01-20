# coding: utf-8
"""Mambu Activity objects - DEPRECATED LEGACY MODULE.

.. warning::

   DEPRECATED: This module uses Mambu API v1 which is no longer supported.
   This code is maintained only for backwards compatibility with legacy systems.
   It will be removed in a future version of MambuPy.

MambuActivity holds a mambu activity. Don't instantiate this class
directly. Look at MambuActivity pydoc for further info.

MambuActivities holds a list of activities.
"""
import json
import warnings
from builtins import str as unicode
from copy import deepcopy
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..mambugeturl import getmambuurl
from ..mambuutil import (
    OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
    MambuCommError,
    MambuError,
    apipwd,
    apiuser,
    encoded_dict,
    iri_to_uri,
    setup_logging,
    strip_tags,
)

warnings.warn(
    "MambuPy.rest.mambuactivity is deprecated and will be removed in a future version. "
    "Mambu API v1 is no longer supported by Mambu.",
    DeprecationWarning,
    stacklevel=2,
)

logger = setup_logging(__name__)


# =============================================================================
# Utility Classes (from mamburestutils.py)
# =============================================================================


class RequestsCounter(object):
    """Singleton that counts requests.

    If you want to control the number of requests you do to Mambu, you
    may find this counter useful. Since it is a Singleton, every Mambu
    object shares it and increases the amount of requests counted here,
    so you may read it on every Mambu object you have per Python
    session you hold.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(RequestsCounter, cls).__new__(cls, *args, **kwargs)
            cls.requests = []
            cls.cnt = 0
        return cls.__instance

    def add(cls, temp):
        cls.requests.append(temp)
        cls.cnt += 1

    def reset(cls):
        cls.cnt = 0
        cls.requests = []


class MambuStructIterator:
    """Enables iteration for Mambu objects that hold lists."""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.offset = 0

    def __next__(self):
        if self.offset >= len(self.wrapped):
            raise StopIteration
        else:
            item = self.wrapped[self.offset]
            self.offset += 1
            return item

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self


# =============================================================================
# URL Function (from mambugeturl.py)
# =============================================================================


def _get_parameters_url(kwargs):
    """Build URL parameters from kwargs."""
    getparams = []
    for k, v in kwargs.items():
        if v is not None:
            getparams.append("%s=%s" % (k, v))
    return getparams


def getactivitiesurl(dummyId="", *args, **kwargs):
    """Request Activities URL.

    dummyId is used because MambuStruct always requires an Id from an
    entity, but the Mambu API doesn't requires it for Activities,
    because of that dummyId defaults to '', but in practice it is never
    used.

    Currently implemented filter parameters:
    * from
    * to
    * branchID
    * clientId
    * centreID
    * userID
    * loanAccountId
    * groupId
    * limit

    See Mambu official developer documentation for further details.

    .. warning:: API V2: NOT compatible. Apparently not yet implemented.
    """
    getparams = []
    if kwargs:
        try:
            getparams.append("from=%s" % kwargs["fromDate"])
            del kwargs["fromDate"]
        except Exception:
            getparams.append("from=%s" % "1900-01-01")

        try:
            getparams.append("to=%s" % kwargs["toDate"])
            del kwargs["toDate"]
        except Exception:
            hoy = datetime.now().strftime("%Y-%m-%d")
            getparams.append("to=%s" % hoy)

        getparams.extend(_get_parameters_url(kwargs))

    url = (
        getmambuurl(*args, **kwargs)
        + "activities"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


mod_urlfunc = getactivitiesurl


# =============================================================================
# Minimal MambuStruct Base Class
# =============================================================================


class MambuStruct(object):
    """Minimal MambuStruct base for Activities.

    This is a stripped-down version containing only the functionality
    required for MambuActivity and MambuActivities.
    """

    RETRIES = 5

    @staticmethod
    def serialize_fields(data):
        """Turns every attribute of the Mambu object into a string representation."""
        if isinstance(data, MambuStruct):
            return data.serialize_struct()
        try:
            it = iter(data)
        except TypeError:
            return unicode(data)
        if type(it) == type(iter([])):
            return [MambuStruct.serialize_fields(e) for e in it]
        elif type(it) == type(iter({})):
            return {k: MambuStruct.serialize_fields(data[k]) for k in it}
        return unicode(data)

    def __getitem__(self, key):
        """Dict-like key query"""
        return self.attrs[key]

    def __setitem__(self, key, value):
        """Dict-like set"""
        self.attrs[key] = value

    def __delitem__(self, key):
        """Dict-like del key"""
        del self.attrs[key]

    def __hash__(self):
        """Hash of the object"""
        try:
            return hash(self.id)
        except Exception:
            return hash(self.__repr__())

    def __getattribute__(self, name):
        """Object-like get attribute"""
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            attrs = object.__getattribute__(self, "attrs")
            if type(attrs) == list or name not in attrs:
                return object.__getattribute__(self, name)
            return attrs[name]

    def __setattr__(self, name, value):
        """Object-like set attribute"""
        try:
            attrs = object.__getattribute__(self, "attrs")
            if type(attrs) == list:
                raise AttributeError
            try:
                object.__getattribute__(self, name)
            except AttributeError:
                attrs[name] = value
            else:
                raise AttributeError
        except AttributeError:
            object.__setattr__(self, name, value)

    def __repr__(self):
        """Mambu object repr tells the class name and the usual 'id' for it."""
        try:
            return self.__class__.__name__ + " - id: %s" % self.attrs["id"]
        except KeyError:
            return self.__class__.__name__ + " (no standard entity)"
        except AttributeError:
            return (
                self.__class__.__name__
                + " - id: '%s' (not synced with Mambu)" % self.entid
            )
        except TypeError:
            return self.__class__.__name__ + " - len: %s" % len(self.attrs)

    def __str__(self):
        """Mambu object str gives a string representation of the attrs attribute."""
        try:
            return self.__class__.__name__ + " - " + str(self.attrs)
        except AttributeError:
            return repr(self)

    def __len__(self):
        """Length of the attrs attribute."""
        return len(self.attrs)

    def __eq__(self, other):
        """Compare two Mambu objects by EncodedKey."""
        if isinstance(other, MambuStruct):
            try:
                if "encodedKey" not in other.attrs or "encodedKey" not in self.attrs:
                    return NotImplemented
            except AttributeError:
                return NotImplemented
            return other["encodedKey"] == self["encodedKey"]

    def has_key(self, key):
        """Dict-like behaviour"""
        try:
            if type(self.attrs) == dict:
                return key in self.attrs
            else:
                raise AttributeError
        except AttributeError:
            raise NotImplementedError

    def __contains__(self, item):
        """Dict-like and List-like behaviour"""
        return item in self.attrs

    def get(self, key, default=None):
        """Dict-like behaviour"""
        if type(self.attrs) == dict:
            return self.attrs.get(key, default)
        else:
            raise NotImplementedError

    def keys(self):
        """Dict-like behaviour"""
        try:
            return self.attrs.keys()
        except AttributeError:
            raise NotImplementedError

    def items(self):
        """Dict-like behaviour"""
        try:
            return self.attrs.items()
        except AttributeError:
            raise NotImplementedError

    def init(self, attrs={}, *args, **kwargs):
        """Initialize from a dictionary responded by Mambu."""
        self.attrs = attrs
        self.preprocess()
        self.convert_dict_to_attrs(*args, **kwargs)
        self.postprocess()
        try:
            self.entid = self.id
        except (TypeError, AttributeError):
            pass
        try:
            for meth in kwargs["methods"]:
                try:
                    getattr(self, meth)()
                except Exception:  # pragma: no cover
                    # Defensive: silently ignore method execution errors
                    pass
        except Exception:
            pass
        try:
            for propname, propval in kwargs["properties"].items():
                setattr(self, propname, propval)
        except Exception:
            pass

    def serialize_struct(self):
        """Makes a string from each element on the attrs attribute."""
        return MambuStruct.serialize_fields(self.attrs)

    def __copy_args(self, args, kwargs):
        self.__args = deepcopy(args)
        for k, v in kwargs.items():
            self.__kwargs[k] = deepcopy(v)

    def __init__(self, urlfunc, entid="", *args, **kwargs):
        """Initialize a new Mambu object."""
        self.entid = entid
        self.rc = RequestsCounter()

        connect = False

        try:
            self.__debug = kwargs.pop("debug")
        except KeyError:
            self.__debug = False

        try:
            self.__formato_fecha = kwargs.pop("date_format")
        except KeyError:
            self.__formato_fecha = "%Y-%m-%dT%H:%M:%S+0000"

        try:
            self.__data = kwargs.pop("data")
        except KeyError:
            self.__data = None

        try:
            self.__method = kwargs.pop("method")
        except KeyError:
            if self.__data:
                self.__method = "POST"
            else:
                self.__method = "GET"

        try:
            self.__limit = kwargs["limit"]
            self.__inilimit = self.__limit
            kwargs.pop("limit")
        except KeyError:
            self.__limit = 0

        try:
            self.__offset = kwargs["offset"]
            kwargs.pop("offset")
        except KeyError:
            self.__offset = 0

        try:
            self.custom_field_name = kwargs.pop("custom_field_name")
        except KeyError:
            pass

        try:
            self.__user = kwargs.pop("user")
        except (KeyError, AttributeError):
            self.__user = apiuser
        try:
            self.__pwd = kwargs.pop("pwd")
        except (KeyError, AttributeError):
            self.__pwd = apipwd

        self.__headers = {"Accept": "application/vnd.mambu.v1+json"}

        try:
            if kwargs.pop("connect"):
                connect = True
        except KeyError:
            connect = True

        self.__args = ()
        self.__kwargs = {}

        self.__copy_args(args, kwargs)

        self.__urlfunc = urlfunc
        if self.__urlfunc is None:
            return

        if connect:
            self.connect(*args, **kwargs)

    def __request(self, url, user, pwd):
        """Make the HTTP request to Mambu."""
        retry_strategy = Retry(
            total=MambuStruct.RETRIES,
            status_forcelist=[429, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["PUT", "DELETE", "POST", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        logger.debug(
            "%s %s, about to make %s request: url %s, data %s, headers %s",
            self.__class__.__name__,
            self.entid,
            self.__method,
            url,
            self.__data,
            [(k, v) for k, v in self.__headers.items()],
        )

        if self.__data:
            data = json.dumps(encoded_dict(self.__data))
            self.__headers["Content-Type"] = "application/json"
            if self.__method == "PATCH":
                resp = http.patch(
                    url, data=data, headers=self.__headers, auth=(user, pwd)
                )
            else:
                resp = http.post(
                    url, data=data, headers=self.__headers, auth=(user, pwd)
                )
        else:
            if self.__method == "DELETE":
                resp = http.delete(url, headers=self.__headers, auth=(user, pwd))
            else:
                resp = http.get(url, headers=self.__headers, auth=(user, pwd))

        self.rc.add(datetime.now())

        logger.debug(
            "%s %s,response code to %s: %s",
            self.__class__.__name__,
            self.entid,
            self.__method,
            resp,
        )

        return resp

    def __process_jsonresp(self, jsonresp, limit, jsresp):
        window = True
        if type(jsonresp) == list:
            try:
                jsresp.extend(jsonresp)
            except AttributeError:
                jsresp = jsonresp
            if len(jsonresp) < limit:
                window = False
        else:
            jsresp = jsonresp
            self._is_mambu_error(jsresp)
            window = False
        return jsresp, window

    def __request_and_process(self, jsresp, url, user, pwd, limit, offset):
        resp = ""
        try:
            resp = self.__request(url, user, pwd)
            resp.raise_for_status()

            self._raw_response_data = resp.content
            jsonresp = json.loads(resp.content)
            jsresp, window = self.__process_jsonresp(jsonresp, limit, jsresp)
        except requests.exceptions.HTTPError as httpex:
            logger.error(
                "%s %s, HTTPError on %s request: url %s",
                self.__class__.__name__,
                self.entid,
                self.__method,
                url,
            )
            try:
                jsresp = json.loads(resp.content)
            except ValueError:
                cont = resp.content
                raise MambuError(
                    strip_tags(cont.decode())
                    .strip()
                    .replace("\n\n", ": ", 1)
                    .replace("\n", ". ", 1)
                    .replace("\n", " ")
                )
            except Exception as ex:  # pragma: no cover
                # Defensive: json.loads raises ValueError for invalid JSON
                raise MambuError("JSON Error: %s" % repr(ex))

            try:
                self._is_mambu_error(jsresp)
            except AttributeError:  # pragma: no cover
                # Defensive: jsresp always dict after json.loads
                pass
        except requests.exceptions.RetryError as rerr:
            raise MambuCommError(
                "ERROR I can't communicate with Mambu: {}".format(str(rerr))
            )
        except Exception as ex:
            logger.exception(
                "%s %s, Exception: %s", self.__class__.__name__, self.entid, str(ex)
            )
            raise ex

        return jsresp, window

    def _is_mambu_error(self, jsresp):
        if (
            "returnCode" in jsresp
            and "returnStatus" in jsresp
            and jsresp["returnCode"] != 0
        ):
            raise MambuError(jsresp["returnStatus"])
        return False

    def __credentials(self):
        try:
            user = self.__user
        except AttributeError:  # pragma: no cover
            # Defensive: __user always set in __init__
            self.__user = apiuser
            user = self.__user
        try:
            pwd = self.__pwd
        except AttributeError:  # pragma: no cover
            # Defensive: __pwd always set in __init__
            self.__pwd = apipwd
            pwd = self.__pwd
        return user, pwd

    def connect(self, *args, **kwargs):
        """Connect to Mambu and make the REST API request."""
        self.__copy_args(args, kwargs)

        if not self.__urlfunc:
            return

        offset = self.__offset
        window = True
        jsresp = {}
        while window:
            if not self.__limit or self.__limit > OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE:
                limit = OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
            else:
                limit = self.__limit

            user, pwd = self.__credentials()

            urlfunc_params = self.__kwargs.copy()
            if self.__method == "GET" and not self.__data:
                urlfunc_params["limit"] = limit
                urlfunc_params["offset"] = offset
            url = iri_to_uri(
                self.__urlfunc(str(self.entid), *self.__args, **urlfunc_params)
            )
            self.__url = url

            jsresp, window = self.__request_and_process(
                jsresp, url, user, pwd, limit, offset
            )

            offset = offset + limit
            if self.__limit:
                self.__limit -= limit
                if self.__limit <= 0:
                    window = False
                    self.__limit = self.__inilimit

        if ("documents" not in url) and self.__method not in ["PATCH", "DELETE"]:
            if type(iter(jsresp)) == type(iter([])):
                logger.debug(
                    "%s, url %s, %s retrieved",
                    self.__class__.__name__,
                    url,
                    len(jsresp),
                )
            self.init(attrs=jsresp, *self.__args, **self.__kwargs)

    def _process_fields(self):
        """Default info massage to appropriate format/style."""
        try:
            for k, v in self.items():
                try:
                    self[k] = v.strip()
                except Exception:
                    pass
        except NotImplementedError:
            pass

    def preprocess(self):
        """Preprocess hook."""
        self._process_fields()

    def postprocess(self):
        """Postprocess hook."""
        self._process_fields()

    def _convert_data_to_pytype(self, data):
        """Convert data to Python built-in types."""
        try:
            d = int(data)
            if str(d) != data:
                return data
            return d
        except (TypeError, ValueError):
            try:
                return float(data)
            except (TypeError, ValueError):
                try:
                    return self.util_date_format(data)
                except (TypeError, ValueError):
                    return data
        return data

    def _convert_dict_to_pytypes(self, data):
        """Recursively convert fields to Python objects."""
        constantFields = [
            "id",
            "groupName",
            "name",
            "homePhone",
            "mobilePhone1",
            "phoneNumber",
            "postcode",
            "emailAddress",
            "description",
        ]
        try:
            it = iter(data)
            if type(it) == type(iter({})):
                d = {}
                for k in it:
                    if k in constantFields:
                        d[k] = data[k]
                    else:
                        d[k] = self._convert_dict_to_pytypes(data[k])
                data = d
            if type(it) == type(iter([])):
                data = [self._convert_dict_to_pytypes(e) for e in it]
        except TypeError:
            pass
        except Exception as ex:  # pragma: no cover
            # Defensive: re-raise unexpected exceptions
            raise ex
        return self._convert_data_to_pytype(data)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """Convert each element on attrs to a proper Python object."""
        self.attrs = self._convert_dict_to_pytypes(self.attrs)

    def util_date_format(self, field, formato=None):
        """Convert a datetime field to a datetime using specified format."""
        if not formato:
            try:
                formato = self.__formato_fecha
            except AttributeError:
                formato = "%Y-%m-%dT%H:%M:%S+0000"
        return datetime.strptime(
            datetime.strptime(field, "%Y-%m-%dT%H:%M:%S+0000").strftime(formato),
            formato,
        )


# =============================================================================
# Activity Classes
# =============================================================================


class MambuActivity(MambuStruct):
    """A loan Activity from Mambu.

    Don't instantiate this class directly. It's mostly used by
    MambuActivities to configure each of its elements as
    MambuActivity objects.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Initialize the MambuStruct."""
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        """Show the activityid of the activity."""
        try:
            return self.__class__.__name__ + " - activityid: %s" % self["activity"]
        except KeyError:
            return self.__class__.__name__ + " (no activity key)"


class MambuActivities(MambuStruct):
    """A list of loan Activities from Mambu."""

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """Convert each element of the list to a MambuActivity object."""
        for n, a in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mambuactivityclass
            except AttributeError:
                self.mambuactivityclass = MambuActivity

            activity = self.mambuactivityclass(urlfunc=None, entid=None, *args, **kwargs)
            activity.init(a, *args, **kwargs)
            activity._MambuStruct__urlfunc = getactivitiesurl
            self.attrs[n] = activity
