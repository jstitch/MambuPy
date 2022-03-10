"""Basic Struct for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuStruct
   MambuEntity
   MambuEntitySearchable
   MambuEntityAttachable
   MambuEntityCF
"""

import copy
import json
from datetime import datetime

from ..mambuutil import (OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, MambuError,
                         MambuPyError, dateFormat)
from .classes import GenericClass, MambuMapObj
from .interfaces import MambuAttachable, MambuSearchable
from .mambuconnector import MambuConnectorREST
from .vos import MambuDocument, MambuValueObject


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

    def __init__(self, **kwargs):
        super().__init__(cf_class=MambuEntityCF, **kwargs)

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
                        if k in constantFields or (len(k) > 2 and k[-3:] == "Key"):
                            d[k] = data[k]
                            if tzdata and k in tzdata:
                                del tzdata[k]
                        else:
                            try:
                                d[k] = convert(data[k], tzdata[k])
                                if type(d[k]) not in [dict, list, datetime]:
                                    del tzdata[k]
                                elif isinstance(d[k], datetime):
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
                        elif isinstance(d, datetime):
                            tzdata[num] = datetime.fromisoformat(tzdata[num]).tzname()
                        l.append(d)
                    data = l
            except TypeError:
                pass
            except Exception as ex:  # pragma: no cover
                # unknown exception
                raise ex

            # Python built-in types: ints, floats, or even datetimes. If it
            # cannot convert it to a built-in type, leave it as string, or
            # as-is. There may be nested Mambu objects here!
            # This are the recursion base cases!
            if data in ["TRUE", "true", "FALSE", "false"]:
                return data.lower() == "true"
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
                if isinstance(data, datetime):
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
                    for (e, te) in zip(it, tzdata):
                        l.append(convert(e, te))
                else:
                    for e in it:
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

    def _extractCustomFields(self, attrs=None):
        """Loops through every custom field set and extracts custom field values
        on the root of the _attrs property."""

        if not attrs:
            attrs = self._attrs

        for attr, val in [atr for atr in attrs.items() if atr[0][0] == "_"]:
            if type(iter(val)) == type(iter({})):
                for key, value in val.items():
                    attrs[key] = self._cf_class(
                        value, "/{}/{}".format(attr, key), "STANDARD"
                    )
            elif type(iter(val)) == type(iter([])):
                attrs[attr[1:]] = self._cf_class(
                    copy.deepcopy(val), "/{}".format(attr), "GROUPED"
                )
                for ind, value in enumerate(val):
                    if type(iter(value)) == type(iter({})):
                        for key, subvalue in value.items():
                            if key[0] != "_":
                                mecf = self._cf_class(
                                    subvalue,
                                    "/{}/{}/{}".format(attr, ind, key),
                                    "GROUPED",
                                )
                                attrs[key + "_" + str(ind)] = mecf
                                # attrs[attr[1:]][ind][key] = mecf
                    else:
                        raise MambuPyError(
                            "CustomFieldSet {} is not a list of dictionaries!".format(
                                attr
                            )
                        )
            else:
                raise MambuPyError("CustomFieldSet {} is not a dictionary!".format(attr))

    def _updateCustomFields(self):
        """Loops through every custom field set and update custom field values
        with the corresponding property at the root of the _attrs dict, then
        deletes the property at root"""
        cfs = []
        # updates customfieldsets
        for attr, val in [atr for atr in self._attrs.items() if atr[0][0] == "_"]:
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
                        for key in value.keys():
                            if key[0] != "_":
                                try:
                                    if self[key + "_" + str(ind)] in [True, False]:
                                        self[key + "_" + str(ind)] = str(
                                            self[key + "_" + str(ind)]
                                        ).upper()
                                    if self[attr][ind][key] != self[key + "_" + str(ind)]:
                                        self[attr[1:]][ind][key] = self[
                                            key + "_" + str(ind)
                                        ]
                                    cfs.append(key + "_" + str(ind))
                                except KeyError:
                                    pass
                try:
                    self._attrs[attr] = copy.deepcopy(self[attr[1:]])
                    cfs.append(attr[1:])
                except KeyError:
                    pass
            else:
                raise MambuPyError(
                    "CustomFieldSet {} is not a dictionary or list of dictionaries!".format(
                        attr
                    )
                )
        # deletes _attrs root keys of custom fields
        for field in cfs:
            del self._attrs[field]


class MambuEntity(MambuStruct):
    """A Mambu object that you may work with directly on Mambu web too."""

    _prefix = ""
    """prefix constant for connections to Mambu"""

    _connector = MambuConnectorREST()
    """Default connector (REST)"""

    @classmethod
    def _get_several(cls, get_func, **kwargs):
        """get several entities.

        Using certain mambu connector function and its particular arguments.

        arg limit has a hard limit imposed by Mambu, that only 1,000 registers
        can be retrieved, so a pagination must be done to retrieve more
        registries.

        A pagination algorithm (using the offset and the 1,000 limitation) is
        applied here so that limit may be higher than 1,000 and _get_several
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
        if "offset" in kwargs and kwargs["offset"] is not None:
            offset = kwargs["offset"]
        else:
            offset = 0
        if "limit" in kwargs and kwargs["limit"] is not None:
            ini_limit = kwargs["limit"]
        else:
            ini_limit = 0

        params = copy.copy(kwargs)
        if "detailsLevel" not in params:
            params["detailsLevel"] = "BASIC"
        window = True
        attrs = []
        while window:
            if not ini_limit or ini_limit > OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE:
                limit = OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
            else:
                limit = ini_limit

            params["offset"] = offset
            params["limit"] = limit if limit != 0 else None
            resp = get_func(cls._prefix, **params)

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
            elem._detailsLevel = params["detailsLevel"]
            elements.append(elem)

        return elements

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
            entid, prefix=cls._prefix, detailsLevel=detailsLevel
        )

        instance = cls.__call__()
        instance._resp = resp
        instance._attrs = dict(json.loads(resp.decode()))
        instance._tzattrs = dict(json.loads(resp.decode()))
        instance._convertDict2Attrs()
        instance._extractCustomFields()
        instance._detailsLevel = detailsLevel

        return instance

    def refresh(self, detailsLevel=""):
        """get again this single entity, identified by its entid.

        Updates _attrs with responded data. Loses any change on _attrs that
        overlaps with anything from Mambu. Leaves alone any other properties
        that don't come in the response.

        Args:
          detailsLevel (str BASIC/FULL) - ask for extra details or not
        """
        if not detailsLevel:
            detailsLevel = self._detailsLevel
        self._resp = self._connector.mambu_get(
            self.id, prefix=self._prefix, detailsLevel=detailsLevel
        )

        self._attrs.update(dict(json.loads(self._resp.decode())))
        self._tzattrs = dict(json.loads(self._resp.decode()))
        self._convertDict2Attrs()
        self._extractCustomFields()
        self._detailsLevel = detailsLevel

    @classmethod
    def get_all(
        cls,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None,
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
        params = {
            "filters": filters,
            "offset": offset,
            "limit": limit,
            "paginationDetails": paginationDetails,
            "detailsLevel": detailsLevel,
            "sortBy": sortBy,
        }

        return cls._get_several(cls._connector.mambu_get_all, **params)

    def update(self):
        """updates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        self._updateCustomFields()
        self._serializeFields()
        try:
            self._connector.mambu_update(
                self.id, self._prefix, copy.deepcopy(self._attrs)
            )
            # should I refresh _attrs? (either get request from Mambu or using the response)
        except MambuError as merr:
            raise merr
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()

    def create(self):
        """creates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        self._updateCustomFields()
        self._serializeFields()
        try:
            self._resp = self._connector.mambu_create(
                self._prefix, copy.deepcopy(self._attrs)
            )
            self._attrs.update(dict(json.loads(self._resp.decode())))
            self._tzattrs = dict(json.loads(self._resp.decode()))
            self._detailsLevel = "FULL"
        except MambuError as merr:
            raise merr
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()

    def patch(self, fields=None, autodetect_remove=False):
        """patches a mambu entity

        Allows patching of parts of the entity up to Mambu.

        fields is a list of the values in the _attrs that will be sent to Mambu

        autodetect automatically searches for deleted fields and patches a
        remove in Mambu.

        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.

        Args:
          fields (list of str) - list of ids of fields to explicitly patch
          autodetect_remove (bool) - False: if deleted fields, don't remove them
                                     True: if delete field, remove them

        Autodetect operation, for any field
        (every field if fields param is None):
          ADD: in attrs, but not in resp
          REPLACE: in attrs, and in resp
          REMOVE: not in attrs, but in resp
          MOVE is not yet implemented (how to autodetect?
                                       request needs 'from' element)

        Raises:
          MambuPyError if field not in attrrs, and not in resp
        """
        # customfields:
        # standard, as other fields (path includes CFset)
        #   REPLACE and REMOVE includes CF in path after CFset
        # grouped:
        #  ADD value is a list of CFs (they queue at end of group)
        #  REPLACE and REMOVE need index in path after CFset,
        #    CF at last replaces/removes just some field in the CFset at the index
        #  remove may have just index in path (removes entire CF)
        #    just CFset in path (removes entire group)
        #  you cannot add or replace entire CF (like by using just the index)

        def extract_path(attrs_dict, field, cf_class):
            if attrs_dict[field].__class__.__name__ == cf_class.__name__:
                return attrs_dict[field]["path"]
            else:
                return "/" + field

        if not fields:
            fields = []
        try:
            # build fields_ops param with what detected using previous rules
            # strings: (OP, PATH) (remove) or (OP, PATH, VALUE) (all else)
            fields_ops = []
            original_attrs = dict(json.loads(self._resp.decode()))
            self._extractCustomFields(original_attrs)
            for field in fields:
                if field in self._attrs.keys() and field not in original_attrs.keys():
                    path = extract_path(self._attrs, field, self._cf_class)
                    try:
                        val = self._attrs[field]["value"]
                    except TypeError:
                        val = self._attrs[field]
                    fields_ops.append(("ADD", path, val))

                elif field in self._attrs.keys() and field in original_attrs.keys():
                    path = extract_path(self._attrs, field, self._cf_class)
                    try:
                        val = self._attrs[field]["value"]
                    except TypeError:
                        val = self._attrs[field]
                    fields_ops.append(("REPLACE", path, val))
                else:
                    raise MambuPyError(
                        "Unrecognizable field {} for patching".format(field)
                    )

            if autodetect_remove:
                for attr in original_attrs.keys():
                    if attr not in self._attrs.keys():
                        path = extract_path(original_attrs, attr, self._cf_class)
                        fields_ops.append(("REMOVE", path))

            self._updateCustomFields()
            self._serializeFields()
            self._connector.mambu_patch(self.id, self._prefix, fields_ops)
            # should I refresh _attrs? (needs get request from Mambu)
        except MambuError as merr:
            raise merr
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()

class MambuEntitySearchable(MambuStruct, MambuSearchable):
    """A Mambu object with seraching capabilities."""

    @classmethod
    def search(
        cls,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
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
        params = {
            "filterCriteria": filterCriteria,
            "sortingCriteria": sortingCriteria,
            "offset": offset,
            "limit": limit,
            "paginationDetails": paginationDetails,
            "detailsLevel": detailsLevel,
        }

        return cls._get_several(cls._connector.mambu_search, **params)


class MambuEntityAttachable(MambuStruct, MambuAttachable):
    """A Mambu object with attaching capabilities."""

    _ownerType = ""
    """attachments owner type of this entity"""

    _attachments = {}
    """dict of attachments of an entity, key is the id"""

    def attach_document(self, filename, title="", notes=""):
        """uploads an attachment to this entity

        Args:
          filename (str) - path and filename of file to upload as attachment
          title (str) - name to assign to the attached file in Mambu
          notes (str) - notes to associate to the attached file in Mambu

        Returns:
          Mambu's response with metadata of the attached document
        """
        response = self._connector.mambu_upload_document(
            owner_type=self._ownerType,
            entid=self.id,
            filename=filename,
            name=title,
            notes=notes,
        )

        doc = MambuDocument(**dict(json.loads(response.decode())))
        self._attachments[str(doc["id"])] = doc

        return response


class MambuEntityCF(MambuValueObject):
    """A Mambu CustomField obtained via an Entity.

    This is NOT a CustomField obtained through it's own endpoint, those go in
    another separate class.

    Here you just have a class to manage custom field values living inside some
    Mambu entity.
    """

    def __init__(self, value, path="", typecf="STANDARD"):
        if typecf not in ["STANDARD", "GROUPED"]:
            raise MambuPyError("invalid CustomField type!")
        self._attrs = {"value": value, "path": path, "type": typecf}
        self._cf_class = GenericClass
