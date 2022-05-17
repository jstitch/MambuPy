"""Mambu Entities

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""
import copy
import json
import time

from .classes import GenericClass
from .interfaces import MambuWritable, MambuAttachable, MambuSearchable
from .mambuconnector import MambuConnectorREST
from .mambustruct import MambuStruct
from .vos import MambuDocument, MambuValueObject
from ..mambuutil import (OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, MambuError,
                         MambuPyError)


class MambuEntity(MambuStruct):
    """A Mambu object that you may work with directly on Mambu web too."""

    _prefix = ""
    """prefix constant for connections to Mambu"""

    _connector = MambuConnectorREST()
    """Default connector (REST)"""

    _filter_keys = [
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
    ]
    """allowed fields for get_all sorting"""

    def __init__(self, **kwargs):
        super().__init__(cf_class=MambuEntityCF, **kwargs)

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

        Args:
          get_func (function): mambu request function that returns several
                                entities (json [])
          kwargs (dict): keyword arguments to pass on to get_func as arguments

            - prefix (str): prefix for connections to Mambu

          kwargs (dict): keyword arguments to pass on to get_func as params

            - detailsLevel (str): "BASIC" or "FULL"
            - offset (int): >= 0
            - limit (int): >= 0 If limit=0 or None, the algorithm will retrieve
                           EVERYTHING according to the given filters, using
                           several requests to that end.

          kwargs (dict): keyword arguments for this method

            - get_entities (bool): should MambuPy automatically instantiate
                                   other MambuPy entities found inside the
                                   retrieved entities?
            - debug (bool): print debugging info

        Returns:
          list of instances of an entity with data from Mambu, assembled from
          possibly several calls to get_func
        """
        init_t = time.time()

        if "offset" in kwargs and kwargs["offset"] is not None:
            offset = kwargs["offset"]
        else:
            offset = 0
        if "limit" in kwargs and kwargs["limit"] is not None:
            ini_limit = kwargs["limit"]
        else:
            ini_limit = 0

        if "prefix" in kwargs and kwargs["prefix"] is not None:
            prefix = kwargs.pop("prefix")
        else:
            prefix = cls._prefix

        if "get_entities" in kwargs and kwargs["get_entities"] is not None:
            get_entities = kwargs.pop("get_entities")
        else:
            get_entities = False

        if "debug" in kwargs and kwargs["debug"] is not None:
            debug = kwargs.pop("debug")
        else:
            debug = False

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
            resp = get_func(prefix, **params)

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
            elem._tzattrs = copy.deepcopy(attr)
            elem._convertDict2Attrs()
            elem._extractCustomFields()
            elem._extractVOs(
                get_entities=get_entities, debug=debug)
            entities = copy.deepcopy(elem._entities)
            if get_entities:
                elem._assignEntObjs(
                    entities,
                    params["detailsLevel"],
                    get_entities,
                    debug=debug)
            elem._detailsLevel = params["detailsLevel"]
            elements.append(elem)


        fin_t = time.time()
        interval = fin_t - init_t
        hours, remainder = divmod(interval, 3600)
        minutes = remainder // 60
        seconds = round(remainder - (minutes * 60), 2)
        if debug:
            print("{}-{} ({}) {}:{}:{}".format(
                elements[0].__class__.__name__,
                elements[0]["id"],
                len(elements),
                int(hours), int(minutes), seconds))

        return elements

    @classmethod
    def get(cls, entid, detailsLevel="BASIC", get_entities=False, **kwargs):
        """get, a single entity, identified by its entid.

        Args:
          entid (str): ID for the entity
          detailsLevel (str BASIC/FULL): ask for extra details or not
          get_entities (bool): should MambuPy automatically instantiate other
                               MambuPy entities found inside the retrieved
                               entity?
          kwargs (dict): keyword arguments for this method

            - debug (bool): print debugging info

        Returns:
          instance of an entity with data from Mambu
        """
        init_t = time.time()

        if "debug" in kwargs and kwargs["debug"]:
            debug = True
        else:
            debug = False

        resp = cls._connector.mambu_get(
            entid, prefix=cls._prefix, detailsLevel=detailsLevel
        )

        instance = cls.__call__()
        instance._resp = resp
        instance._attrs = dict(json.loads(resp.decode()))
        instance._tzattrs = dict(json.loads(resp.decode()))
        instance._convertDict2Attrs()
        instance._extractCustomFields()
        instance._extractVOs(
            get_entities=get_entities, debug=debug)
        entities = copy.deepcopy(instance._entities)
        if get_entities:
            instance._assignEntObjs(
                entities,
                detailsLevel,
                get_entities,
                debug=debug)
        instance._detailsLevel = detailsLevel

        fin_t = time.time()
        interval = fin_t - init_t
        hours, remainder = divmod(interval, 3600)
        minutes = remainder // 60
        seconds = round(remainder - (minutes * 60), 2)
        if debug:
            print("{}-{} {}:{}:{}".format(
                instance.__class__.__name__,
                instance["id"],
                int(hours), int(minutes), seconds))

        return instance

    def refresh(self, detailsLevel=""):
        """get again this single entity, identified by its entid.

        Updates _attrs with responded data. Loses any change on _attrs that
        overlaps with anything from Mambu. Leaves alone any other properties
        that don't come in the response.

        Args:
          detailsLevel (str BASIC/FULL): ask for extra details or not
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
        self._extractVOs()
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
        **kwargs
    ):
        """get_all, several entities, filtering allowed

        Args:
          filters (dict): key-value filters, dependes on each entity
                          (keys must be one of the _filter_keys)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results (fields must be one of the _sortBy_fields)
          kwargs (dict): extra parameters that a specific entity may receive in
                         its get_all method

        Returns:
          list of instances of an entity with data from Mambu
        """
        if filters and isinstance(filters, dict):
            for filter_k in filters.keys():
                if filter_k not in cls._filter_keys:
                    raise MambuPyError(
                        "key {} not in allowed _filterkeys: {}".format(
                            filter_k, cls._filter_keys
                        )
                    )

        if sortBy and isinstance(sortBy, str):
            for sort in sortBy.split(","):
                for num, part in enumerate(sort.split(":")):
                    if num == 0 and part not in cls._sortBy_fields:
                        raise MambuPyError(
                            "field {} not in allowed _sortBy_fields: {}".format(
                                part, cls._sortBy_fields
                            )
                        )

        params = {
            "filters": filters,
            "offset": offset,
            "limit": limit,
            "paginationDetails": paginationDetails,
            "detailsLevel": detailsLevel,
            "sortBy": sortBy,
        }
        if kwargs:
            params.update(kwargs)

        return cls._get_several(cls._connector.mambu_get_all, **params)


class MambuEntityWritable(MambuStruct, MambuWritable):
    """A Mambu object with writing capabilities."""

    def update(self):
        """updates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        self._updateVOs()
        self._updateCustomFields()
        self._serializeFields()
        try:
            self._connector.mambu_update(
                self.id, self._prefix, copy.deepcopy(self._attrs)
            )
            # should I refresh _attrs? (either get request from Mambu or using the response)
        except MambuError:
            raise
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()
            self._extractVOs()

    def create(self):
        """creates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        self._updateVOs()
        self._updateCustomFields()
        self._serializeFields()
        try:
            self._resp = self._connector.mambu_create(
                self._prefix, copy.deepcopy(self._attrs)
            )
            self._attrs.update(dict(json.loads(self._resp.decode())))
            self._tzattrs = dict(json.loads(self._resp.decode()))
            self._detailsLevel = "FULL"
        except MambuError:
            raise
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()
            self._extractVOs()

    def patch(self, fields=None, autodetect_remove=False):
        """patches a mambu entity

        Allows patching of parts of the entity up to Mambu.

        fields is a list of the values in the _attrs that will be sent to Mambu

        autodetect automatically searches for deleted fields and patches a
        remove in Mambu.

        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.

        Args:
          fields (list of str): list of ids of fields to explicitly patch
          autodetect_remove (bool): False: if deleted fields, don't remove them
                                    True: if delete field, remove them

        Autodetect operation, for any field (every field if fields param is
        None):
          * ADD: in attrs, but not in resp
          * REPLACE: in attrs, and in resp
          * REMOVE: not in attrs, but in resp
          * MOVE: not yet implemented (how to autodetect? request needs 'from' element)

        Raises:
          `MambuPyError`: if field not in attrrs, and not in resp
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

            self._updateVOs()
            self._updateCustomFields()
            self._serializeFields()
            self._connector.mambu_patch(self.id, self._prefix, fields_ops)
            # should I refresh _attrs? (needs get request from Mambu)
        except MambuError:
            raise
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()
            self._extractVOs()


class MambuEntitySearchable(MambuStruct, MambuSearchable):
    """A Mambu object with searching capabilities."""

    @classmethod
    def search(
        cls,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        **kwargs
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
        if kwargs:
            params.update(kwargs)

        return cls._get_several(cls._connector.mambu_search, **params)


class MambuEntityAttachable(MambuStruct, MambuAttachable):
    """A Mambu object with attaching capabilities."""

    _ownerType = ""
    """attachments owner type of this entity"""

    _attachments = {}
    """dict of attachments of an entity, key is the id"""

    def attach_document(self, filename, title="", notes=""):
        """uploads an attachment to this entity

        _attachments dicitionary gets a new entry with the attached document.

        Args:
          filename (str): path and filename of file to upload as attachment
          title (str): name to assign to the attached file in Mambu
          notes (str): notes to associate to the attached file in Mambu

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

    def get_attachments_metadata(
        self,
        offset=None, limit=None,
        paginationDetails="OFF",
    ):
        """Gets metadata for all the documents attached to an entity

        _attachments dicitionary is cleaned and set with attached documents.

        Args:
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination

        Returns:
          Mambu's response with metadata of the attached documents
        """
        self._attachments = {}

        response = self._connector.mambu_get_documents_metadata(
            entid=self.id,
            owner_type=self._ownerType,
            offset=offset, limit=limit, paginationDetails=paginationDetails)

        metadata_list = json.loads(response.decode())

        for metadata in metadata_list:
            doc = MambuDocument(**metadata)
            self._attachments[str(doc["id"])] = doc

        return response

    def del_attachment(self, documentName=None, documentId=None):
        """deletes an attachment by its documentName.

        Args:
          documentName (str): optional, the name (title)
                              of the document to be deleted
          documentid (str): optional, the id of the document to be deleted

        Raises:
          `MambuPyError`: if the documentId and the documentName is not an
                          attachment of the entity
        """
        if not documentId and not documentName:
            raise MambuPyError(
                "You must provide a documentId or a documentName")
        docid = None
        docbyname = None
        if documentName:
            try:
                docbyname = [
                    attach for attach in self._attachments.values()
                    if attach["name"] == documentName][0]
                docid = docbyname["id"]
            except IndexError:
                raise MambuPyError(
                    "Document name '{}' is not an attachment of {}".format(
                        documentName,
                        repr(self)))
        if documentId:
            try:
                self._attachments[documentId]
                if docid:
                    if docid != documentId:
                        raise MambuPyError(
                            "Document with name '{}' does not has id '{}'".format(
                                documentName, documentId))
                else:
                    docid = documentId
            except KeyError:
                raise MambuPyError(
                    "Document id '{}' is not an attachment of {}".format(
                        documentId,
                        repr(self)))

        self._connector.mambu_delete_document(docid)
        self._attachments.pop(docid)


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


class MambuInstallment(MambuStruct):
    """Loan Account Installment (aka Repayment)"""
    def __repr__(self):
        """repr tells the class name, the number, the state and the dueDate
        """
        return self.__class__.__name__ + " - #{}, {}, {}".format(
            self._attrs["number"],
            self._attrs["state"],
            self._attrs["dueDate"].strftime("%Y-%m-%d"))
