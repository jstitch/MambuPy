"""Basic Struct for Mambu Objects."""

import copy
from datetime import datetime
import json

from .mambuconnector import MambuConnectorREST

from ..mambuutil import (
    dateFormat,
    MambuError,
    MambuPyError,
    OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
    )


class MambuMapObj():
    """An object with dictionary-like behaviour for key-value data"""

    def __init__(self, **kwargs):
        self._attrs = {}
        if kwargs:
            for key, val in kwargs.items():
                self._attrs[key] = val

    def __getattribute__(self, name):
        """Object-like get attribute

        When accessing an attribute, tries to find it in the _attrs
        dictionary, so now MambuMapObj may act not only as a dict-like
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
                # magic won't happen when not a dict-like MambuMapObj or
                # when _attrs has not the 'name' key (this last one means
                # that if 'name' is not a property of the object too,
                # AttributeError will raise by default)
                return object.__getattribute__(self, name)
            # all else, read the property from the _attrs dict, but with a . syntax
            # if a MambuEntityCF, just return its value
            if _attrs[name].__class__.__name__ == "MambuEntityCF":
                return _attrs[name]["value"]
            return _attrs[name]

    def __setattr__(self, name, value):
        """Object-like set attribute

        When setting an attribute, tries to set it in the _attrs
        dictionary, so now MambuMapObj acts not only as a dict-like
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
                    # when not treating with a dict-like MambuMapObj...
                    raise AttributeError
                try:
                    # see if 'name' is currently a property of the object
                    object.__getattribute__(self, name)
                except AttributeError:
                    # if not, then assign it as a new key in the dict
                    if (name in _attrs and
                        _attrs[name].__class__.__name__ == "MambuEntityCF"
                    ):
                        _attrs[name] = MambuEntityCF(value)
                    else:
                        _attrs[name] = value
                else:  # pragma: no cover
                    raise AttributeError
            except AttributeError:
                # all else assign it as a property of the object
                object.__setattr__(self, name, value)

    def __getitem__(self, key):
        """Dict-like key query"""
        # if a MambuEntityCF, just return its value
        if self._attrs[key].__class__.__name__ == "MambuEntityCF":
            return self._attrs[key]["value"]
        return self._attrs[key]

    def __setitem__(self, key, value):
        """Dict-like set"""
        # if no _attrs attribute, should be automatically created?
        if (key in self._attrs and
            self._attrs[key].__class__.__name__ == "MambuEntityCF"
            ):
            self._attrs[key] = MambuEntityCF(value)
        else:
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
            return self.__class__.__name__ + " - " + str(self._attrs)
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

    TimeZones info:
    convertDict2Attrs loses TZ info on datetime fields.

    We will save them on _tzattrs field. Prefering this method since this allows
    comparison with datetimes on your code without needing TZ initialized.

    For example:

`today = datetime.now()`
`loan.creationDate < today`

    That code works since now() doesn't have any TZ info.

    If cretionDate has TZ info in it, you could not make the comparison.

    So, we need to preserve the TZ info somewhere else. Since TZ info is the
    same for ALL the Mambu instance, you can extract it from any datetime
    object. creationDate works almost all the time. You can change it on your
    own implementation of any MambuEntity. And you can set it as None if you
    really (really?) wish to lose TZ info.
    """

    _tzattrs = {}

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
            entid, prefix=cls._prefix, detailsLevel=detailsLevel)

        instance = cls.__call__()
        instance._resp = resp
        instance._attrs = dict(json.loads(resp.decode()))
        instance._tzattrs = dict(json.loads(resp.decode()))
        instance._convertDict2Attrs()
        instance._extractCustomFields()

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
            elem._convertDict2Attrs()
            elem._extractCustomFields()
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

    def attach_document(self, filename, title="", notes=""):
        """uploads an attachment to this entity

        Args:
          filename (str) - path and filename of file to upload as attachment
          title (str) - name to assign to the attached file in Mambu
          notes (str) - notes to associate to the attached file in Mambu

        Returns:
          Mambu's response with metadata of the attached document
        """
        if not hasattr(self, "_ownerType"):
            raise MambuPyError(
                "{} entity does not supports attachments!".format(
                    self.__class__.__name__))
        return self._connector.mambu_upload_document(
            owner_type=self._ownerType,
            entid=self.id,
            filename=filename,
            name=title,
            notes=notes)

    def update(self, *args, **kwargs):
        """ updates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        self._updateCustomFields()
        self._serializeFields()
        try:
            self._connector.mambu_update(self.id, self._prefix, self._attrs)
        except MambuError as merr:
            raise merr
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()

    def _convertDict2Attrs(self, *args, **kwargs):
        """Each element on the atttrs attribute gest converted to a
        proper python object, depending on type.

        Some default constantFields are left as is (strings), because they are
        better treated as strings. This includes any field whose name ends with
        'Key'.
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
        # and any field whose name ends with "Key"

        def convert(data, tzdata=None):
            """Recursively convert the fields on the data given to a python object."""
            # Iterators, lists and dictionaries
            # Here comes the recursive calls!
            try:
                it = iter(data)
                if type(it) == type(iter({})):
                    d = {}
                    for k in it:
                        if k in constantFields or (len(k)>2 and k[-3:]=="Key"):
                            d[k] = data[k]
                            if tzdata and k in tzdata:
                                del tzdata[k]
                        else:
                            try:
                                d[k] = convert(data[k], tzdata[k])
                                if type(d[k]) not in [dict, list, datetime]:
                                    del tzdata[k]
                                elif type(d[k]) == datetime:
                                    tzdata[k] = datetime.fromisoformat(tzdata[k]).tzname()
                            except (KeyError, ValueError, TypeError):
                                d[k] = convert(data[k])
                    data = d
                if type(it) == type(iter([])):
                    l = []
                    for num, (e, te) in enumerate(zip(it, tzdata)):
                        d = convert(e, te)
                        if type(d) not in [dict, list, datetime]:
                            tzdata[num] = None
                        elif type(d) == datetime:
                            tzdata[num] = datetime.fromisoformat(tzdata[num]).tzname()
                        l.append(d)
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
            if data in ["TRUE", "FALSE", "true", "false"]:
                return True if data in ["TRUE", "true"] else False
            try:
                d = int(data)
                if (
                    str(d) != data
                ):  # if string has trailing 0's, leave it as string, to not lose them
                    return data
                return d
            except (TypeError, ValueError):
                try:
                    f_data = float(data)
                    return f_data
                except (TypeError, ValueError):
                    try:
                        return dateFormat(data)
                    except (TypeError, ValueError):
                        return data

            return data

        self._attrs = convert(self._attrs, self._tzattrs)

    def _serializeFields(self, *args, **kwargs):
        """Every attribute of the Mambu object is turned in to a string
        representation.

        If the object is an iterable one, it goes down to each of its
        elements and turns its attributes too, recursively.

        The base case is when it's a MambuMapObj class (this one) so it
        just 'serializes' the attr atribute.

        All datetimes are converted using timezone information stored in the
        object.

        Skips every MambuMapObj owned by this entity.
        """
        def convert(data, tzdata=None):
            """Recursively convert the fields on the data given to a python object."""
            if isinstance(data, MambuMapObj):
                return data
            try:
                it = iter(data)
            except TypeError:
                if type(data) == datetime:
                    data_asdate = data.isoformat()
                    if tzdata:
                        data_asdate += tzdata[-6:]
                    return data_asdate
                if data in [True, False]:
                    return str(data).lower()
                return str(data)

            if type(it) == type(iter([])):
                l = []
                if tzdata:
                    for num, (e, te) in enumerate(zip(it, tzdata)):
                        l.append(convert(e, te))
                else:
                    for num, e in enumerate(it):
                        l.append(convert(e))
                return l
            elif type(it) == type(iter({})):
                d = {}
                for k in it:
                    if tzdata and k in tzdata:
                        d[k] = convert(data[k], tzdata[k])
                    else:
                        d[k] = convert(data[k])
                return d
            # elif ... tuples? sets?
            return data

        self._attrs = convert(self._attrs, self._tzattrs)

    def _extractCustomFields(self):
        """Loops through every custom field set and extracts custom field values
        on the root of the _attrs property."""

        for attr, val in [atr for atr in self._attrs.items() if atr[0][0]=="_"]:
            if type(iter(val)) == type(iter({})):
                for key, value in val.items():
                    self[key] = MambuEntityCF(value)
            elif type(iter(val)) == type(iter([])):
                self[attr[1:]] = MambuEntityCF(copy.deepcopy(val))
                for ind, value in enumerate(val):
                    if type(iter(value)) == type(iter({})):
                        for key, subvalue in value.items():
                            if key[0] != "_":
                                mecf = MambuEntityCF(subvalue)
                                self[key+"_"+str(ind)] = mecf
                                # self[attr[1:]][ind][key] = mecf
                    else:
                        raise MambuPyError(
                            "CustomFieldSet {} is not a list of dictionaries!".format(attr))
            else:
                raise MambuPyError(
                    "CustomFieldSet {} is not a dictionary!".format(attr))

    def _updateCustomFields(self):
        """Loops through every custom field set and update custom field values
        with the corresponding property at the root of the _attrs dict, then
        deletes the property at root"""
        cfs = []
        # updates customfieldsets
        for attr, val in [atr for atr in self._attrs.items() if atr[0][0]=="_"]:
            if type(iter(val)) == type(iter({})):
                for key in val.keys():
                    try:
                        if self[key] in [True, False]:
                            self[key] = str(self[key]).upper()
                        self._attrs[attr][key] = self[key]
                        cfs.append(key)
                    except KeyError:
                        pass
            elif type(iter(val)) == type(iter([])):
                for ind, value in enumerate(val):
                    if type(iter(value)) == type(iter({})):
                        for key, subvalue in value.items():
                            if key[0] != "_":
                                if self[key+"_"+str(ind)] in [True, False]:
                                    self[key+"_"+str(ind)] = str(
                                        self[key+"_"+str(ind)]).upper()
                                if self[attr][ind][key] != self[key+"_"+str(ind)]:
                                    self[attr[1:]][ind][key] = self[key+"_"+str(ind)]
                                cfs.append(key+"_"+str(ind))
                try:
                    self._attrs[attr] = copy.deepcopy(self[attr[1:]])
                    cfs.append(attr[1:])
                except KeyError:
                    pass
            else:
                raise MambuPyError(
                    "CustomFieldSet {} is not a dictionary or list of dictionaries!".format(attr))
        # deletes _attrs root keys of custom fields
        for field in cfs:
            del self._attrs[field]


class MambuEntity(MambuStruct):
    """A Mambu object that you may work with directly on Mambu web too."""

    _prefix = ""
    """prefix constant for connections to Mambu"""


class MambuValueObject(MambuMapObj):
    """A Mambu object with some schema but that you won't interact directly
    with in Mambu web, but through some entity."""


class MambuEntityCF(MambuValueObject):
    """A Mambu CustomField obtained via an Entity.

    This is NOT a CustomField obtained through it's own endpoint, those go in
    another separate class.

    Here you just have a class to manage custom field values living inside some
    Mambu entity.
    """

    def __init__(self, value):
        self._attrs = {"value": value}
