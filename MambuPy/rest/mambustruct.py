# coding: utf-8
"""Base class for all Mambu objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

Includes functionality to download such objects using GET requests to
Mambu, and to POST requests to Mambu.

Some caching may be achieved. Please look at caching done at
mambuproduct.AllMambuProducts class for an example of how caching should
be done.

Official Mambu dev documentation at Mambu Developer Center:
https://developer.mambu.com

You must configure your Mambu client in mambuconfig.py Please read the
pydocs there for more information.

Some basic definitions:

* MambuStruct refers to the parent class of all Mambu Objects and

* MambuPy Mambu objects refers to any child of MambuStruct, usually defined at
  some mambu-somename- python module file. Sometimes referred as implemented
  MambuStruct or something fancy

* Mambu entity refers to an entity retrieved via a request via Mambu REST
  API. It's a more abstract thing in fact. Also may refer to entities on a
  relational database but the term table is preferred in this case.
"""
import json
import time
from builtins import str as unicode
from datetime import datetime

import requests
from future.utils import implements_iterator
from copy import deepcopy

from ..mambuutil import (OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, MambuCommError,
                         MambuError, apipwd, apiuser, encoded_dict, iri_to_uri,
                         strip_tags)


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


@implements_iterator
class MambuStructIterator:
    """Enables iteration for some Mambu objects that may want to have iterators.

    Loans, Transactions, Repayments, Clients, Groups, Users, Branches
    are some of the Mambu entitites that may be iterable. Here at
    MambuPy, all of them have an iterator class for requesting several
    entitites to Mambu, instead of just one of them. Please refer to
    each MambuObject pydoc for more info.
    """

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


class MambuStruct(object):
    """This one is the Father of all Mambu objects at MambuPy.

    It's a dictionary-like structure by default, self.attr attribute
    holds all the info respondend by Mambu REST API.

    This object is flexible enough to hold a list instead of a
    dictionary for certain objects holding iterators.

    Further work is needed to hold list-like behaviour however.
    """

    RETRIES = 5
    """This one holds the maximum number of retries for requests to Mambu.

    Some networks have a lot of lag, so a safe maximum has been added
    here. If after RETRIES attempts to connect to Mambu, MambuPy can't
    connect, a MambuCommError will be raised.
    """

    @staticmethod
    def serialize_fields(data):
        """Turns every attribute of the Mambu object in to a string representation.

        If the object is an iterable one, it goes down to each of its
        elements and turns its attributes too, recursively.

        The base case is when it's a MambuStruct class (this one) so it
        just 'serializes' the attr atribute. Refer to
        MambuStruct.serialize_struct pydoc.

        This is perhaps the worst way to do it, still looking for a better way.
        """
        if isinstance(data, MambuStruct):
            return data.serialize_struct()
        try:
            it = iter(data)
        except TypeError:
            return unicode(data)
        if type(it) == type(iter([])):
            l = []
            for e in it:
                l.append(MambuStruct.serialize_fields(e))
            return l
        elif type(it) == type(iter({})):
            d = {}
            for k in it:
                d[k] = MambuStruct.serialize_fields(data[k])
            return d
        # elif ... tuples? sets?
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
        """Object-like get attribute

        When accessing an attribute, tries to find it in the attrs
        dictionary, so now MambuStruct may act not only as a dict-like
        structure, but as a full object-like too (this is the getter
        side).
        """
        try:
            # first, try to read 'name' as if it's a property of the object
            # if it doesn't exists as property, AttributeError raises
            return object.__getattribute__(self, name)
        except AttributeError:
            # try to read the attrs property
            attrs = object.__getattribute__(self, "attrs")
            if type(attrs) == list or name not in attrs:
                # magic won't happen when not a dict-like MambuStruct or
                # when attrs has not the 'name' key (this last one means
                # that if 'name' is not a property of the object too,
                # AttributeError will raise by default)
                return object.__getattribute__(self, name)
            # all else, read the property from the attrs dict, but with a . syntax
            return attrs[name]

    def __setattr__(self, name, value):
        """Object-like set attribute

        When setting an attribute, tries to set it in the attrs
        dictionary, so now MambuStruct acts not only as a dict-like
        structure, but as a full object-like too (this is the setter
        side).
        """
        try:
            # attrs needs to exist to make the magic happen!
            # ... if not, AttributeError raises
            attrs = object.__getattribute__(self, "attrs")
            if type(attrs) == list:
                # when not treating with a dict-like MambuStruct...
                raise AttributeError
            try:
                # see if 'name' is currently a property of the object
                object.__getattribute__(self, name)
            except AttributeError:
                # if not, then assign it as a new key in the dict
                attrs[name] = value
            else:
                raise AttributeError

        # all else, assign it as a property of the object
        except AttributeError:
            object.__setattr__(self, name, value)

    def __repr__(self):
        """Mambu object repr tells the class name and the usual 'id' for it.

        If an iterable, it instead gives its length.
        """
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
        """Length of the attrs attribute.

        If dict-like (not iterable), it's the number of keys holded on the attrs dictionary.
        If list-like (iterable), it's the number of elements of the attrs list.
        """
        return len(self.attrs)

    def __eq__(self, other):
        """Very basic way to compare to Mambu objects.

                Only looking at their EncodedKey field (its primary key on the
                Mambu DB).

        .. todo:: a lot of improvements may be done here.
        """
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
                raise AttributeError  # if attrs is not a dict
        except AttributeError:  # if attrs doesnt exist
            raise NotImplementedError

    def __contains__(self, item):
        """Dict-like and List-like behaviour"""
        return item in self.attrs

    def get(self, key, default=None):
        """Dict-like behaviour"""
        if type(self.attrs) == dict:
            return self.attrs.get(key, default)
        else:
            raise NotImplementedError  # if attrs is not a dict

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
        """Default initialization from a dictionary responded by Mambu

        in to the elements of the Mambu object.

        It assings the response to attrs attribute and converts each of
        its elements from a string to an adequate python object: number,
        datetime, etc.

        Basically it stores the response on the attrs attribute, then
        runs some customizable preprocess method, then runs
        convert_dict_to_attrs method to convert the string elements to an
        adequate python object, then a customizable postprocess method.

        It also executes each method on the 'methods' attribute given on
        instantiation time, and sets new customizable 'properties' to
        the object.

        Why not on __init__? two reasons:

        * __init__ optionally connects to Mambu, if you don't connect to
          Mambu, the Mambu object will be configured but it won't have
          any Mambu info on it. Only when connected, the Mambu object
          will be initialized, here.

          Useful to POST several times the same Mambu object. You make a
          POST request over and over again by calling it's connect()
          method every time you wish. This init method will configure the
          response in to the attrs attribute each time.

          You may also wish to update the info on a previously initialized
          Mambu object and refresh it with what Mambu now has. Instead of
          building a new object, you just connect() again and it will be
          refreshed.

        * Iterable Mambu objects (lists) do not initialize here, the
          iterable Mambu object __init__ goes through each of its elements
          and then initializes with this code one by one. Please look at
          some Mambu iterable object code and pydoc for more details."""
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
                except Exception:
                    pass
        except Exception:
            pass
        try:
            for propname, propval in kwargs["properties"].items():
                setattr(self, propname, propval)
        except Exception:
            pass

    def serialize_struct(self):
        """Makes a string from each element on the attrs attribute.

                Read the class attribute MambuStruct.serialize_fields pydoc for
                more info.

                It DOES NOT serializes the class, for persistence or network
                transmission, just the fields on the attrs attribute.

                Remember that attrs may have any type of elements: numbers,
                strings, datetimes, Mambu objects, etc. This is a way to convert
                it to a string in an easy, however ugly, way.

                WARNING: it may fall in a stack overflow

        .. todo:: check recursion levels.
        """
        serial = MambuStruct.serialize_fields(self.attrs)
        return serial

    def __init__(self, urlfunc, entid="", *args, **kwargs):
        """Initializes a new Mambu object.

        Args:
         urlfunc (str): is the only required parameter. The urlfunc
                           returns a string of the URL to make a request to Mambu. You
                           may read about the valid urlfuncs supported by MambuPy at
                           mambuutil.py
         entid (str): is the usual ID of a Mambu entity you like to GET from
                         Mambu. The ID of a loan account, a client, a group, etc. Or the
                         transactions or repayments of certain loan account. It's an
                         optional parameter because the iterable Mambu objects don't need
                         an specific ID, just some other filtering parameters supported
                         on the urlfunc function.

        If you send a None urlfunc, the object will be configured, but
        won't connect to Mambu, never. Useful for iterables that
        configure their elements but can't or won't need Mambu to send
        further information. See :any:`mamburepayment.MambuRepayments`
        for an example of this.

        Should you need to add support for more functionality, add them
        at mambuutuil.

        Many other arguments may be sent here to further configure the
        Mambu object or the response by Mambu REST API:

        * **debug** flag (currently not implemented, just stored on the object)
        * **connect** flag, to optionally omit the connection to Mambu (see
          the init() (with no underscores) method pydoc)
        * **data** parameter for POST requests (see connect() method pydoc)
        * **date_format** parameter (see util_date_format() method pydoc)

        Also, parameters to be sent to Mambu on the request, such as:

        * **limit** parameter (for pagination, see connect() method
          pydoc). If 0 (default) tells connect to auto-paginate. All
          else is used as given for manual pagination (all along with
          the offset argument too)
        * **offset** parameter (for pagination, see connect() method
          pydoc)
        * **fullDetails**, accountState and other filtering parameters
          (see mambuutil pydocs)
        * **user**, **password**, **url** to connect to Mambu, to bypass
          mambuconfig configurations (see mambuutil pydoc)"""

        self.entid = entid
        """ID of the Mambu entity, or empty if not wanting a specific entity to be GETted"""

        self.rc = RequestsCounter()
        """Request Count Singleton"""

        connect = False
        """Default value connect"""

        try:
            self.__debug = kwargs["debug"]
            """Debug flag.

        .. todo:: not currently furtherly implemented
            """
        except KeyError:
            self.__debug = False

        try:
            self.__formato_fecha = kwargs["date_format"]
            """The default date format to be used for any datettime elements on the attrs attribute.

            Remember to use valid Python datetime strftime formats.
            """
        except KeyError:
            self.__formato_fecha = "%Y-%m-%dT%H:%M:%S+0000"

        try:
            self.__data = kwargs["data"]
            """JSON data to be sent to Mambu for POST/PATCH requests."""
        except KeyError:
            self.__data = None

        try:
            self.__method = kwargs["method"]
            """REST method to use when calling connect"""
        except KeyError:
            self.__method = "GET"

        try:
            self.__limit = kwargs["limit"]
            self.__inilimit = self.__limit
            """Limit the number of elements to be retrieved from Mambu on GET requests.

            Defaults to 0 which means (for the connect method) that you
            don't care how many elements Mambu has, you wish to retrieve
            them all.
            """
            kwargs.pop("limit")
        except KeyError:
            self.__limit = 0

        try:
            self.__offset = kwargs["offset"]
            """When retrieving several elements from Mambu on GET
            requests, offset for the first element to be retrieved.
            """
            kwargs.pop("offset")
        except KeyError:
            self.__offset = 0

        try:
            self.custom_field_name = kwargs["custom_field_name"]
            """custom_field_name attribute."""
        except KeyError:
            pass

        self.__headers = {"Accept": "application/vnd.mambu.v1+json"}

        try:
            if kwargs.pop("connect"):
                connect = True
        except KeyError:
            connect = True

        self.__args = ()
        self.__kwargs = {}

        self.__args = deepcopy(args)
        for k, v in kwargs.items():
            self.__kwargs[k] = deepcopy(v)

        self.__urlfunc = urlfunc
        """The given urlfunc argument is saved here.

        It's used at the connect() method, when called.
        """
        if (
            self.__urlfunc == None
        ):  # Only used when GET returns an array, meaning the MambuStruct must be a list of MambuStucts
            return  # and each element is init without further configs. EDIT 2015-07-11: Really?

        if connect:
            self.connect(*args, **kwargs)

    def _make_request(self, url, user, pwd):
        """Method used in connect, for make the request.

        Uses self.__data dictionary to feed the body for POST and PATCH requests.
        If there is no data in self.__data, it defaults to a GET request.

        Args:
            url (str): url to make request, changed with iri_to_uri
            user (str): user to authenticate for requests
            pwd (str): password to authenticate for requests

        Returns:
            The response of the request (json)
        """
        if self.__data:
            data = json.dumps(encoded_dict(self.__data))
            self.__headers["Content-Type"] = "application/json"
            # PATCH
            if self.__method == "PATCH":
                resp = requests.patch(
                    url, data=data, headers=self.__headers, auth=(user, pwd)
                )
            # POST
            else:
                resp = requests.post(
                    url, data=data, headers=self.__headers, auth=(user, pwd)
                )
        else:
            # DELETE
            if self.__method == "DELETE":
                resp = requests.delete(
                    url, headers=self.__headers, auth=(user, pwd)
                )
            # GET
            else:
                resp = requests.get(
                    url, headers=self.__headers, auth=(user, pwd)
                )
        return resp

    def connect(self, *args, **kwargs):
        """Connect to Mambu, make the request to the REST API.

                If there's no urlfunc to use, nothing is done here.

                When done, initializes the attrs attribute of the Mambu object
                by calling the init method. Please refer to that code and pydoc
                for further information.

                Uses urllib module to connect. Since all Mambu REST API
                responses are json, uses json module to translate the response
                to a valid python object (dictionary or list).

                When Mambu returns a response with returnCode and returnStatus
                fields, it means something went wrong with the request, and a
                MambuError is thrown detailing the error given by Mambu itself.

                If you need to make a POST request, send a data argument to the
                new Mambu object.

                Provides to prevent errors due to using special chars on the
                request URL. See mambuutil.iri_to_uri() method pydoc for further
                info.

                Provides to prevent errors due to using special chars on the
                parameters of a POST request. See mambuutil.encoded_dict()
                method pydoc for further info.

                For every request done, the request counter Singleton is
                increased.

                Includes retry logic, to provide for a max number of connection
                failures with Mambu. If maximum retries are reached,
                MambuCommError is thrown.

                Includes pagination code. Mambu supports a max of 500 elements
                per response. Such an ugly detail is wrapped here so further
                pagination logic is not needed above here. You need a million
                elements? you got them by making several 500 elements requests
                later joined together in a sigle list. Just send a limit=0
                (default) and that's it.

        .. todo:: improve raised exception messages. Sometimes
                  MambuCommErrors are thrown due to reasons not always
                  clear when catched down the road, but that perhaps may
                  be noticed in here and aren't fully reported to the
                  user. Specially serious on retries-MambuCommError
                  situations (the except Exception that increases the
                  retries counter is not saving the exception message,
                  just retrying).

        .. todo:: what about using decorators for the retry and for the
                  window logic?
                  (https://www.oreilly.com/ideas/5-reasons-you-need-to-learn-to-write-python-decorators
                  # Reusing impossible-to-reuse code)
        """
        self.__args = deepcopy(args)
        for k, v in kwargs.items():
            self.__kwargs[k] = deepcopy(v)

        jsresp = {}

        if not self.__urlfunc:
            return

        # Pagination window, Mambu restricts at most 500 elements in response
        offset = self.__offset
        window = True
        jsresp = {}
        while window:
            if not self.__limit or self.__limit > OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE:
                limit = OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
            else:
                limit = self.__limit

            # Retry mechanism, for awful connections
            retries = 0
            while retries < MambuStruct.RETRIES:
                try:
                    # Basic authentication
                    user = self.__kwargs.get("user", apiuser)
                    pwd = self.__kwargs.get("pwd", apipwd)
                    url = iri_to_uri(
                        self.__urlfunc(
                            str(self.entid),
                            limit=limit,
                            offset=offset,
                            *self.__args,
                            **self.__kwargs
                        )
                    )
                    self.__url = url

                    # Return a response, default Get
                    resp = self._make_request(url, user, pwd)

                    # Always count a new request when done!
                    self.rc.add(datetime.now())
                    try:
                        self._raw_response_data = resp.content
                        jsonresp = json.loads(resp.content)
                        # Returns list: extend list for offset
                        if type(jsonresp) == list:
                            try:
                                jsresp.extend(jsonresp)
                            except AttributeError:
                                # First window, forget that jsresp was a dict, turn it in to a list
                                jsresp = jsonresp
                            if len(jsonresp) < limit:
                                window = False
                        # Returns dict: in theory Mambu REST API doesn't takes limit/offset in to account
                        else:
                            jsresp = jsonresp
                            window = False
                    except ValueError as ex:
                        # json.loads invalid data argument
                        try:
                            cont = str(resp.content, "utf-8")
                        except TypeError:
                            cont = resp.content
                        if "502" in cont or "503" in cont or "504" in cont:
                            time.sleep(1)
                            retries += 1
                        else:
                            raise MambuError(
                                strip_tags(cont)
                                .strip()
                                .replace("\n\n", ": ", 1)
                                .replace("\n", ". ", 1)
                                .replace("\n", " ")
                            )
                    except Exception as ex:
                        # any other json error
                        raise MambuError("JSON Error: %s" % repr(ex))
                    else:
                        # if we reach here, we're done and safe
                        break
                except MambuError as merr:
                    raise merr
                except requests.exceptions.RequestException:
                    retries += 1
                except Exception as ex:
                    """unknown exception"""
                    raise ex
            else:
                raise MambuCommError("ERROR I can't communicate with Mambu")

            # next window, moving offset...
            offset = offset + limit
            if self.__limit:
                self.__limit -= limit
                if self.__limit <= 0:
                    window = False
                    self.__limit = self.__inilimit

        try:
            if (
                "returnCode" in jsresp
                and "returnStatus" in jsresp
                and jsresp["returnCode"] != 0
            ):
                raise MambuError(jsresp["returnStatus"])
        except AttributeError:
            pass

        if ("documents" not in url) and self.__method not in ["PATCH", "DELETE"]:
            self.init(attrs=jsresp, *self.__args, **self.__kwargs)

    def _request_with_method(self, method, data, *args, **kwargs):
        """Method to do a specific request on the current Mambu entity"""
        self._MambuStruct__method = method
        self._MambuStruct__data = data
        self.connect(*args, **kwargs)
        self._MambuStruct__method = "GET"
        self._MambuStruct__data = None
        return 1

    def _process_fields(self):
        """Default info massage to appropiate format/style.

        This processing is called on preprocess and postprocess, AKA
        before and after conversion of fields to appropiate
        format/style.

        Perfect example: custom fields on certain objects is a mess
        (IMHO) when retrieved from Mambu, so some easiness is
        implemented here to access them. See some of this objects
        modules and pydocs for further info.

        Tasks done here:

        - Each custom field is given a 'name' key that holds the field
          name, and for each keyed name, the value of the custom field is
          assigned. Each pair of custom field name/value is entered as a
          new property on the main dictionary, allowing an easy access to
          them, not nested inside a pretty dark 'customInformation/Values'
          list.

        - Every item on the attrs dictionary gets stripped from trailing
          spaces (useful when users make typos).

        PLEASE REMEMBER! whenever you call postprocess on inherited
        classes you should call this method too, or else you lose the
        effect of the tasks done here.
        """
        def massage_appropiate_format():
            if self.has_key(self.custom_field_name):
                self[self.custom_field_name] = [
                    c
                    for c in self[self.custom_field_name]
                    if c["customField"]["state"] != "DEACTIVATED"
                ]
                for custom in self[self.custom_field_name]:
                    field_name = custom["customField"]["name"]
                    field_id = custom["customField"]["id"]
                    if custom["customFieldSetGroupIndex"] != -1:
                        field_name += "_" + str(custom["customFieldSetGroupIndex"])
                        field_id += "_" + str(custom["customFieldSetGroupIndex"])
                    custom["name"] = field_name
                    custom["id"] = field_id
                    try:
                        self[field_name] = custom["value"]
                        self[field_id] = custom["value"]
                    except KeyError:
                        self[field_name] = custom["linkedEntityKeyValue"]
                        self[field_id] = custom["linkedEntityKeyValue"]
                        custom["value"] = custom["linkedEntityKeyValue"]
        try:
            try:
                massage_appropiate_format()
            # in case you don't have any custom_field_name, don't do anything here
            except (AttributeError, TypeError):
                pass

            for k, v in self.items():
                try:
                    self[k] = v.strip()
                except Exception:
                    pass
        except NotImplementedError:
            pass

    def preprocess(self):
        """Each MambuStruct implementation may massage the info on the
        Mambu response before conversion to an appropiate format/style
        adequate for its needs.
        """
        self._process_fields()

    def postprocess(self):
        """Each MambuStruct implementation may massage the info on the
        Mambu response after conversion to an appropiate format/style
        adequate for its needs.
        """
        self._process_fields()

    def _convert_data_to_pytype(self, data):
        """"Python built-in types: ints, floats, or even datetimes.
        If it cannot convert it to a built-in type, leave it as string,
        or as-is. There may be nested Mambu objects here!
        This are the recursion base cases!
        """
        try:
            d = int(data)
            if (
                str(d) != data
            ):  # if string has trailing 0's, leave it as string, to not lose them
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
        """Recursively convert the fields on the data given to a python object."""

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
        # Iterators, lists and dictionaries
        # Here comes the recursive calls!
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
                l = []
                for e in it:
                    l.append(self._convert_dict_to_pytypes(e))
                data = l
        except TypeError:
            pass
        except Exception as ex:
            """unknown exception"""
            raise ex
        return self._convert_data_to_pytype(data)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """Each element on the attrs attribute gest converted to a
        proper python object, depending on type.

        Some default constantFields are left as is (strings), because
        they are better treated as strings.
        """
        self.attrs = self._convert_dict_to_pytypes(self.attrs)

    def util_date_format(self, field, formato=None):
        """Converts a datetime field to a datetime using some specified format.

        What this really means is that, if specified format includes
        only for instance just year and month, day and further info gets
        ignored and the objects get a datetime with year and month, and
        day 1, hour 0, minute 0, etc.

        A useful format may be %Y%m%d, then the datetime objects
        effectively translates into date objects alone, with no relevant
        time information.

        PLEASE BE AWARE, that this may lose useful information for your
        datetimes from Mambu. Read this for why this may be a BAD idea:
        https://julien.danjou.info/blog/2015/python-and-timezones
        """
        if not formato:
            try:
                formato = self.__formato_fecha
            except AttributeError:
                formato = "%Y-%m-%dT%H:%M:%S+0000"
        return datetime.strptime(
            datetime.strptime(field, "%Y-%m-%dT%H:%M:%S+0000").strftime(formato),
            formato,
        )

    def create(self, data, *args, **kwargs):
        """Creates an entity in Mambu

        This method must be implemented in child classes

        Args:
            data (dictionary): dictionary with data to send, this dictionary
                               is specific for each Mambu entity
        """
        # if module of the function is diferent from the module of the object
        # that means create is not implemented in child class
        if self.create.__func__.__module__ != self.__module__:
            raise Exception("Child method not implemented")

        return self._request_with_method("POST", data, *args, **kwargs)

    def update(self, data, *args, **kwargs):
        """Downloads an update made to an entity in Mambu.

        This method must be implemented in child classes.

        Args:
            data (dictionary): data to send
        """
        if self.update.__func__.__module__ != self.__module__:
            raise NotImplementedError

        self.connect(*args, **kwargs)
        return 1

    def update_patch(self, data, *args, **kwargs):
        """Updates an entity in Mambu

        This method must be implemented in child classes

        Args:
            data (dictionary): dictionary with data to send, this dictionary
                               is specific for each Mambu entity
        """
        # if module of the function is diferent from the module of the object
        # that means create is not implemented in child class
        if self.update_patch.__func__.__module__ != self.__module__:
            raise NotImplementedError

        if not data:
            raise Exception("Requires data to update")

        return self._request_with_method("PATCH", data, *args, **kwargs)

    def update_post(self, data, *args, **kwargs):
        """Updates an entity in Mambu

        This method must be implemented in child classes

        Args:
            data (dictionary): dictionary with data to send, this dictionary
                               is specific for each Mambu entity
        """
        # if module of the function is diferent from the module of the object
        # that means create is not implemented in child class
        if self.update_post.__func__.__module__ != self.__module__:
            raise Exception("Child method not implemented")
        if not data:
            raise Exception("Requires data to update")

        return self._request_with_method("POST", data, *args, **kwargs)

    def upload_document(self, data, *args, **kwargs):
        """Uploads a document in Mambu

        This method must be implemented in child classes
        https://support.mambu.com/docs/attachments-api#post-attachments

        Args:
            data (dictionary): dictionary with data to send
        Example:
        data = {
            "document":{
                "documentHolderKey"     : self.encodedKey,
                "documentHolderType"    : "LOAN_ACCOUNT", # CLIENT, GROUP, USER, BRANCH...
                "name"                  : "loan_resume",
                "type"                  : "pdf",
            },
            "documentContent"           : "['encodedBase64_file']",
        }
        """
        # if module of the function is diferent from the module of the object
        # that means create is not implemented in child class
        if self.upload_document.__func__.__module__ != self.__module__:
            raise Exception("Child method not implemented")
        if not data:
            raise Exception("Requires data to upload")

        return self._request_with_method("POST", data, *args, **kwargs)

def set_custom_field(mambuentity, customfield="", *args, **kwargs):
    """Modifies the customField field for the given object with
    something related to the value of the given field.

    If the dataType == "USER_LINK" then instead of using the value
    of the CF, it will be a MambuUser object.

    Same if dataType == "CLIENT_LINK", but with a MambuClient.

    Default case: just uses the same value the CF already had.

    Returns the number of requests done to Mambu.
    """
    from . import mambuclient, mambuuser

    try:
        customFieldValue = mambuentity[customfield]
        # find the dataType customfield by name or id
        datatype = [
            l["customField"]["dataType"]
            for l in mambuentity[mambuentity.custom_field_name]
            if (l["name"] == customfield or l["id"] == customfield)
        ][0]
    except IndexError:
        # if no customfield found with the given name, assume it is a grouped
        # custom field, name must have an index suffix that must be removed
        try:
            # find the dataType customfield by name or id
            datatype = [
                l["customField"]["dataType"]
                for l in mambuentity[mambuentity.custom_field_name]
                if (
                    l["name"] == customfield.split("_")[0]
                    or l["id"] == customfield.split("_")[0]
                )
            ][0]
        except IndexError:
            err = MambuError(
                "Object %s has no custom field '%s'" % (mambuentity["id"], customfield)
            )
            raise err
    except AttributeError:
        err = MambuError("Object does not have a custom field to set")
        raise err

    if datatype == "USER_LINK":
        mambuentity[customfield] = mambuuser.MambuUser(
            entid=customFieldValue, *args, **kwargs
        )
    elif datatype == "CLIENT_LINK":
        mambuentity[customfield] = mambuclient.MambuClient(
            entid=customFieldValue, *args, **kwargs
        )
    else:
        mambuentity[customfield] = customFieldValue
        return 0
    return 1
