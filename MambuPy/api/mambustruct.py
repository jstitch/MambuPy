"""Basic Struct for Mambu Objects."""

import copy
import json

from .mambuconnector import MambuConnectorREST

from ..mambuutil import (
    dateFormat,
    OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
    )


class MambuMapObj():
    """An object with dictionary-like behaviour for key-value data"""

    def __init__(self):
        self._attrs = {}

    def __getattribute__(self, name):
        """Object-like get attribute

        When accessing an attribute, tries to find it in the _attrs
        dictionary, so now MambuStruct may act not only as a dict-like
        structure, but as a full object-like too (this is the getter
        side).
        """
        try:
            # first, try to read 'name' as if it's a property of the object
            # if it doesn't exists as property, AttributeError raises
            return object.__getattribute__(self, name)
        except AttributeError:
            # try to read the _attrs property
            _attrs = object.__getattribute__(self, "_attrs")
            if type(_attrs) == list or name not in _attrs:
                # magic won't happen when not a dict-like MambuStruct or
                # when _attrs has not the 'name' key (this last one means
                # that if 'name' is not a property of the object too,
                # AttributeError will raise by default)
                return object.__getattribute__(self, name)
            # all else, read the property from the _attrs dict, but with a . syntax
            return _attrs[name]

    def __setattr__(self, name, value):
        """Object-like set attribute

        When setting an attribute, tries to set it in the _attrs
        dictionary, so now MambuStruct acts not only as a dict-like
        structure, but as a full object-like too (this is the setter
        side).
        """
        # if name beginning with _, assign it as a property of the object
        if name[0] == "_":
            object.__setattr__(self, name, value)
        else:
            try:
                # _attrs needs to exist to make the magic happen!
                # ... if not, AttributeError raises
                _attrs = object.__getattribute__(self, "_attrs")
                if type(_attrs) == list:
                    # when not treating with a dict-like MambuStruct...
                    raise AttributeError
                try:
                    # see if 'name' is currently a property of the object
                    object.__getattribute__(self, name)
                except AttributeError:
                    # if not, then assign it as a new key in the dict
                    _attrs[name] = value
                else:  # pragma: no cover
                    raise AttributeError
            except AttributeError:
                # all else assign it as a property of the object
                object.__setattr__(self, name, value)

    def __getitem__(self, key):
        """Dict-like key query"""
        return self._attrs[key]

    def __setitem__(self, key, value):
        """Dict-like set"""
        # if no _attrs attribute, should be automatically created?
        self._attrs[key] = value

    def __delitem__(self, key):
        """Dict-like del key"""
        del self._attrs[key]

    def __str__(self):
        """Mambu object str gives a string representation of the _attrs attribute."""
        try:
            return self.__class__.__name__ + " - " + str(self._attrs)
        except AttributeError:
            return repr(self)

    def __repr__(self):
        """Mambu object repr tells the class name and the usual 'id' for it.

        If an iterable, it instead gives its length.
        """
        try:
            return self.__class__.__name__ + " - id: %s" % self._attrs["id"]
        except KeyError:
            return self.__class__.__name__ + " (no standard entity)"
        except AttributeError:
            return (
                self.__class__.__name__
                + " - id: '%s' (not synced with Mambu)" % self.entid
            )
        except TypeError:
            return self.__class__.__name__ + " - len: %s" % len(self._attrs)

    def __eq__(self, other):
        """Very basic way to compare to Mambu objects.

                Only looking at their EncodedKey field (its primary key on the
                Mambu DB).

        .. todo:: a lot of improvements may be done here.
        """
        if isinstance(other, MambuMapObj):
            try:
                if "encodedKey" not in other._attrs or "encodedKey" not in self._attrs:
                    return NotImplemented
            except AttributeError:
                return NotImplemented
            return other["encodedKey"] == self["encodedKey"]

    def __hash__(self):
        """Hash of the object"""
        try:
            return hash(self.encodedKey)
        except AttributeError:
            try:
                return hash(self.__class__.__name__ + self.id)
            except Exception:
                return hash(self.__repr__())

    def __len__(self):
        """Length of the _attrs attribute.

        If dict-like (not iterable), it's the number of keys holded on the _attrs dictionary.
        If list-like (iterable), it's the number of elements of the _attrs list.
        """
        return len(self._attrs)

    def __contains__(self, item):
        """Dict-like and List-like behaviour"""
        return item in self._attrs

    def get(self, key, default=None):
        """Dict-like behaviour"""
        if type(self._attrs) == dict:
            return self._attrs.get(key, default)
        else:
            raise NotImplementedError  # if _attrs is not a dict

    def keys(self):
        """Dict-like behaviour"""
        try:
            return self._attrs.keys()
        except AttributeError:
            raise NotImplementedError

    def items(self):
        """Dict-like behaviour"""
        try:
            return self._attrs.items()
        except AttributeError:
            raise NotImplementedError

    def values(self):
        """Dict-like behaviour"""
        try:
            return self._attrs.values()
        except AttributeError:
            raise NotImplementedError

    def has_key(self, key):
        """Dict-like behaviour"""
        try:
            if type(self._attrs) == dict:
                return key in self._attrs
            else:
                raise AttributeError  # if _attrs is not a dict
        except AttributeError:  # if _attrs doesnt exist
            raise NotImplementedError


class MambuStruct(MambuMapObj):
    """Basic Struct for Mambu Objects.

    Dictionary-like objects.
    """

    _connector = MambuConnectorREST()
    """Default connector (REST)"""

    @classmethod
    def get(cls, entid, detailsLevel="BASIC"):
        """get, a single entity, identified by its entid.

        Args:
          entid (str) - ID for the entity
          detailsLevel (str BASIC/FULL) - ask for extra details or not

        Returns:
          instance of an entity with data from Mambu
        """
        resp = cls._connector.mambu_get(
            entid, url_prefix=cls._prefix, detailsLevel=detailsLevel)

        instance = cls.__call__()
        instance._resp = resp
        instance._attrs = dict(json.loads(resp.decode()))
        instance.convertDict2Attrs()

        return instance

    @classmethod
    def __get_several(cls, get_func, **kwargs):
        """get several entities.

        Using certain mambu connector function and its particular arguments.

        arg limit has a hard limit imposed by Mambu, that only 1,000 registers
        can be retrieved, so a pagination must be done to retrieve more
        registries.

        A pagination algorithm (using the offset and the 1,000 limitation) is
        applied here so that limit may be higher than 1,000 and __get_several
        will get a all the registers from Mambu in several requests.

        If limit=0 or None, the algorithm will retrieve EVERYTHING according to
        the given filters, using several requests to that end.

        Args:
          get_func (function) - mambu request function that returns several
                                entities (json [])
          kwargs (dict) - keyword arguments to pass on to get_func

        Returns:
          list of instances of an entity with data from Mambu, assembled from
          possibly several calls to get_func
        """
        if "offset" in kwargs and kwargs["offset"] != None:
            offset = kwargs["offset"]
        else:
            offset = 0
        if "limit" in kwargs and kwargs["limit"] != None:
            ini_limit = kwargs["limit"]
        else:
            ini_limit = 0

        params = copy.copy(kwargs)
        window = True
        attrs = []
        while window:
            if not ini_limit or ini_limit > OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE:
                limit = OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
            else:
                limit = ini_limit

            params["offset"] = offset
            params["limit"] = limit if limit != 0 else None
            resp = get_func(
                cls._prefix,
                **params)

            jsonresp = list(json.loads(resp.decode()))
            if len(jsonresp) < limit:
                window = False
            attrs.extend(jsonresp)

            # next window, moving offset...
            offset = offset + limit
            if ini_limit:
                ini_limit -= limit
                if ini_limit <= 0:
                    window = False

        elements = []
        for attr in attrs:
            elem = cls.__call__()
            elem._resp = json.dumps(attr).encode()
            elem._attrs = attr
            elem.convertDict2Attrs()
            elements.append(elem)

        return elements

    @classmethod
    def get_all(
        cls,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None
    ):
        """get_all, several entities, filtering allowed

        Args:
          filters (dict) - key-value filters (depends on each entity)
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not
          sortBy (str field:ASC,field2:DESC) - sorting criteria for results

        Returns:
          list of instances of an entity with data from Mambu
        """
        params = {"filters": filters,
                  "offset": offset,
                  "limit": limit,
                  "paginationDetails": paginationDetails,
                  "detailsLevel": detailsLevel,
                  "sortBy": sortBy}

        return cls.__get_several(cls._connector.mambu_get_all, **params)

    # TODO: not all entities are searchable... implement a Searchable interface
    # prop _searchable obj to get the search method, else: NotImplementedError
    @classmethod
    def search(
        cls,
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

        Returns:
          list of instances of an entity with data from Mambu
        """
        params = {"filterCriteria": filterCriteria,
                  "sortingCriteria": sortingCriteria,
                  "offset": offset,
                  "limit": limit,
                  "paginationDetails": paginationDetails,
                  "detailsLevel": detailsLevel}

        return cls.__get_several(cls._connector.mambu_search, **params)

    def convertDict2Attrs(self, *args, **kwargs):
        """Each element on the atttrs attribute gest converted to a
        proper python object, depending on type.

        Some default constantFields are left as is (strings), because
        they are better treated as strings.
        """
        constantFields = [
            "id",
            "groupName",
            "name",
            "homePhone",
            "mobilePhone",
            "mobilePhone2",
            "postcode",
            "emailAddress",
            "description",
        ]

        def convierte(data):
            """Recursively convert the fields on the data given to a python object."""
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
                            d[k] = convierte(data[k])
                    data = d
                if type(it) == type(iter([])):
                    l = []
                    for e in it:
                        l.append(convierte(e))
                    data = l
            except TypeError:
                pass
            except Exception as ex:  # pragma: no cover
                """ unknown exception """
                raise ex

            # Python built-in types: ints, floats, or even datetimes. If it
            # cannot convert it to a built-in type, leave it as string, or
            # as-is. There may be nested Mambu objects here!
            # This are the recursion base cases!
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
                        return dateFormat(data)
                    except (TypeError, ValueError):
                        return data

            return data

        self._attrs = convierte(self._attrs)
