"""Mambu Entities

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy
from importlib import import_module
import json
import logging
import time

from .classes import GenericClass
from .interfaces import (
    MambuWritable,
    MambuAttachable,
    MambuSearchable,
    MambuCommentable,
    MambuOwnable,
)
from .connector.rest import MambuConnectorREST
from .mambustruct import MambuStruct
from .vos import MambuDocument, MambuComment, MambuValueObject
from MambuPy.mambuutil import MambuError, MambuPyError


logger = logging.getLogger(__name__)
logger.propagate = True


class MambuEntity(MambuStruct):
    """A Mambu object that you may work with directly on Mambu web too."""

    _prefix = ""
    """prefix constant for connections to Mambu"""

    _connector = None
    """Default connector (REST)"""

    _filter_keys = []
    """allowed filters for get_all filtering"""

    _sortBy_fields = []
    """allowed fields for get_all sorting"""

    def __init__(self, **kwargs):
        super().__init__(cf_class=MambuEntityCF, **kwargs)
        if "connector" not in kwargs:
            self._connector = MambuConnectorREST(**kwargs)
        else:
            self._connector = kwargs["connector"]

    def __search_field_in_cfsets(self, field):
        """Search for a field in custom field sets for the entity.

        Retrieves all the customfieldsets for this entity and looks if the
        field lives there.

        If field is found, returns the path going through the set.

        Args:
          field (str): the field to search in customfieldsets

        Returns:
          (str): the path for the field when found or None if not found.
        """
        if not hasattr(self, "_mcfs"):
            from .mambucustomfield import MambuCustomFieldSet

            owner_type = getattr(self, "_ownerType", "")
            self._mcfs = MambuCustomFieldSet.get_all(availableFor=owner_type)
        for cfs in self._mcfs:
            for cf in cfs.customFields:
                if field == cf["id"]:
                    return "/" + cfs.id + "/" + field

    def _extract_field_path(self, field, attrs_dict={}, original_keys=[], cf_class=None):
        """Extracts the path for a given field.

        If the field is a Custom Field, the path is given in a property in its
        attrs dict. (cf `MambuPy.api.entities.MambuEntityCF`)

        If not, first it looks at the original keys in attrs to look if it
        lives in the root (/) of the entity.

        If not, looks for the field in the custom field sets of the entity.

        If not, the path does not exists, but it may be a valid path,
        default to / . Here we are hoping the path is correct,
        otherwise a PATCH may throw an error.

        TODO: perhaps here, in the default case, a better approach
        would be to implement, and maintain, the schema for each
        entity as a VO, and validate if field belongs here. If not,
        default would be an empty string for not being a valid field.

        Args:
          field (str): a field for which to extract the path
          attrs (dict): an attrs structure holding the field
          original_keys (list): keys for entity original attrs
          cf_class (obj): the class used for custom field VOs. If the field is
                          a CF in attrs, the path is a property of it. If not,
                          it lives on the "root" of the attrs

        Returns:
          (str): the path to the field.

        """
        if not cf_class:
            cf_class = self._cf_class
        if not attrs_dict:
            attrs_dict = self._attrs

        if attrs_dict[field].__class__.__name__ == cf_class.__name__:
            return attrs_dict[field]["path"]
        else:
            # perhaps its a field from the original root attributes
            if field in original_keys:
                return "/" + field

            # perhaps its a custom field, search in all CustomFieldSets for
            # this type of entity
            path_from_sets = self.__search_field_in_cfsets(field)
            if path_from_sets:
                return path_from_sets

            # not a CF, not an existing root property, it has no path,
            # try defaulting to root attribute, perhaps entity didn't
            # had it and now we need it to have it
            return "/" + field

    @classmethod
    def __build_object(
        cls,
        connector,
        resp,
        attrs,
        tzattrs,
        get_entities=False,
        detailsLevel="BASIC",
        debug=False,
    ):
        """Builds an instance of an Entity object

        Args:
          cls (obj): the object to build
          connector(obj): connector object to Mambu
          resp (bytes): the raw json that originates the object
          attrs (dict): the dict with the values to build the object
          tzattrs (dict): the dict with TZ data for datetimes in attrs
          get_entities (bool): should MambuPy automatically instantiate other
                               MambuPy entities found inside the built entity?
          detailsLevel (str): "BASIC" or "FULL"
          debug (bool): print debugging info
        """
        instance = cls.__call__(connector=connector)
        instance._resp = resp
        instance._attrs = attrs
        instance._tzattrs = tzattrs
        instance._convertDict2Attrs()
        instance._extractCustomFields()
        instance._extractVOs(get_entities=get_entities, debug=debug)
        entities = copy.deepcopy(instance._entities)
        if get_entities:
            instance._assignEntObjs(entities, detailsLevel, get_entities, debug=debug)
        instance._detailsLevel = detailsLevel

        return instance

    @classmethod
    def __get_several_args(cls, args, get_entities=False, debug=False):
        """Processes `MambuPy.api.entities.get_several` arguments.

        Args:
          cls (obj): the object for which the args are built
          args (dict): optional arguments received by get_several method
        """
        if "prefix" in args and args["prefix"] is not None:
            prefix = args.pop("prefix")
        else:
            prefix = cls._prefix

        if "get_entities" in args and args["get_entities"] is not None:
            get_entities = args.pop("get_entities")

        if "debug" in args and args["debug"] is not None:
            debug = args.pop("debug")

        params = copy.copy(args)
        if "detailsLevel" not in params:
            params["detailsLevel"] = "BASIC"

        return prefix, get_entities, debug, params

    @classmethod
    def _get_several(cls, get_func, connector, **kwargs):
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
          connector (obj): connector object to Mambu
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

        (prefix, get_entities, debug, params) = cls.__get_several_args(kwargs)

        logger.debug("request several entities %s", cls.__name__)
        list_resp = get_func(prefix, **params)
        jsonresp = list(json.loads(list_resp.decode()))
        logger.debug("%s, %s retrieved", cls.__name__, len(jsonresp))

        elements = []
        for attr in jsonresp:
            # builds the Entity object
            elem = cls.__build_object(
                connector=connector,
                resp=json.dumps(attr).encode(),
                attrs=attr,
                tzattrs=copy.deepcopy(attr),
                get_entities=get_entities,
                detailsLevel=params["detailsLevel"],
                debug=debug,
            )
            elements.append(elem)

        fin_t = time.time()
        interval = fin_t - init_t
        hours, remainder = divmod(interval, 3600)
        minutes = remainder // 60
        seconds = round(remainder - (minutes * 60), 2)
        if debug:
            print(
                "{}-{} ({}) {}:{}:{}".format(
                    elements[0].__class__.__name__,
                    elements[0]["id"],
                    len(elements),
                    int(hours),
                    int(minutes),
                    seconds,
                )
            )

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
          kwargs (dict): keyword arguments for this method.
                         May include a user, pwd and url to connect to Mambu.

            - debug (bool): print debugging info

        Returns:
          instance of an entity with data from Mambu
        """
        init_t = time.time()

        if "debug" in kwargs and kwargs["debug"]:
            debug = True
        else:
            debug = False

        connector = MambuConnectorREST(**kwargs)
        logger.debug("request entity %s %s", cls.__name__, entid)
        resp = connector.mambu_get(entid, prefix=cls._prefix, detailsLevel=detailsLevel)

        # builds the Entity object
        instance = cls.__build_object(
            connector=connector,
            resp=resp,
            attrs=dict(json.loads(resp.decode())),
            tzattrs=dict(json.loads(resp.decode())),
            get_entities=get_entities,
            detailsLevel=detailsLevel,
            debug=debug,
        )

        fin_t = time.time()
        interval = fin_t - init_t
        hours, remainder = divmod(interval, 3600)
        minutes = remainder // 60
        seconds = round(remainder - (minutes * 60), 2)
        if debug:
            print(
                "{}-{} {}:{}:{}".format(
                    instance.__class__.__name__,
                    instance["id"],
                    int(hours),
                    int(minutes),
                    seconds,
                )
            )

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
                         its get_all method. May include a user, pwd and url to
                         connect to Mambu.

        Returns:
          list of instances of an entity with data from Mambu
        """
        if filters:
            for filter_k in [fk for fk in filters.keys() if fk not in cls._filter_keys]:
                raise MambuPyError(
                    "key {} not in allowed _filterkeys: {}".format(
                        filter_k, cls._filter_keys
                    )
                )

        if sortBy:
            for sort in sortBy.split(","):
                for num, part in [
                    (n, p)
                    for n, p in enumerate(sort.split(":"))
                    if (n == 0 and p not in cls._sortBy_fields)
                ]:
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

        connector = MambuConnectorREST(**kwargs)
        return cls._get_several(connector.mambu_get_all, connector, **params)


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

    def __patch_op(self, operation, attrs, original_keys, field, cf_class):
        """Returns a patch operation tuple.

        Args:
          operation (str): One of ADD, REPLACE or REMOVE (MOVE not supproted yet)
          attrs (dict): the attrs structure holding the field
          original_keys (list): original keys for the entity attrs
          field (str): the field for which to apply a patch operation
          cf_class (obj): the class used for custom field VOs

        Returns:
          (tuple): according to the PATCH operation
          None: in case the field is not a valid attribute to patch
        """
        path = self._extract_field_path(field, attrs, original_keys, cf_class)
        if not path:
            return
        if operation == "REMOVE":
            return (operation, path)
        try:
            val = attrs[field]["value"]
        except (TypeError, KeyError):
            val = attrs[field]
        return (operation, path, val)

    def __patch_field_op(self, field, original_attrs):
        """Returns a valid ADD or REPLACE operation tuple for a field in attrs."""
        if field in self._attrs.keys() and field not in original_attrs.keys():
            # op says if this is an actual field or CF to
            # patch. If it's not, DO NOHTING
            op = self.__patch_op(
                "ADD", self._attrs, original_attrs.keys(), field, self._cf_class
            )
            if op:
                return op
        elif field in self._attrs.keys() and field in original_attrs.keys():
            return self.__patch_op(
                "REPLACE", self._attrs, original_attrs.keys(), field, self._cf_class
            )
        else:
            raise MambuPyError("Unrecognizable field {} for patching".format(field))

    def patch(self, fields=None, autodetect_remove=False):
        """patches a mambu entity

        Allows patching of parts of the entity up to Mambu.

        fields is a list of the keys in the _attrs that will be sent to Mambu

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

        if not fields:
            fields = []
        try:
            # build fields_ops param with what detected using previous rules
            # strings: (OP, PATH) (remove) or (OP, PATH, VALUE) (all else)
            fields_ops = []
            original_attrs = dict(json.loads(self._resp.decode()))
            self._extractCustomFields(original_attrs)
            self._updateVOs()
            for field in fields:
                field_op = self.__patch_field_op(field, original_attrs)
                if field_op:
                    fields_ops.append(field_op)
                else:
                    raise MambuPyError("You cannot patch {} field".format(field))
            if autodetect_remove:
                for attr in [
                    att for att in original_attrs.keys() if att not in self._attrs.keys()
                ]:
                    fields_ops.append(
                        self.__patch_op(
                            "REMOVE", original_attrs, original_attrs, attr, self._cf_class
                        )
                    )

            self._updateCustomFields()
            self._serializeFields()
            if fields_ops:
                self._connector.mambu_patch(self.id, self._prefix, fields_ops)
            # should I refresh _attrs? (needs get request from Mambu)
        except MambuError:
            raise
        finally:
            self._convertDict2Attrs()
            self._extractCustomFields()
            self._extractVOs()

    def _delete_for_creation(self):
        """Deletes extra fields from Mambu unusable for entity
        creation.

        Implement on entities which require further cleaning.
        """

    def delete(self):
        """deletes a mambu entity.

        Leaves the object in a supposedly state where you can create
        it again. Depends on required custom fields to be present in
        the entity at the moment of deletion.

        TODO: implement some way to ensure schemas are accomplished to
        make sure we can run creation after deletion.
        """
        try:
            self._connector.mambu_delete(self.id, self._prefix)
        except MambuError:
            raise

        # cleaning...
        for key in ["id", "encodedKey"]:
            try:
                del self._attrs[key]
            except KeyError:
                pass
        self._delete_for_creation()


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
                              each entity FilterCriteria schema
          sortingCriteria (dict): fields according to
                            each entity SortingCriteria
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

        connector = MambuConnectorREST(**kwargs)
        return cls._get_several(connector.mambu_search, connector, **params)


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
        offset=None,
        limit=None,
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
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
        )

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
            raise MambuPyError("You must provide a documentId or a documentName")
        docid = None
        docbyname = None
        if documentName:
            try:
                docbyname = [
                    attach
                    for attach in self._attachments.values()
                    if attach["name"] == documentName
                ][0]
                docid = docbyname["id"]
            except IndexError:
                raise MambuPyError(
                    "Document name '{}' is not an attachment of {}".format(
                        documentName, repr(self)
                    )
                )
        if documentId:
            try:
                self._attachments[documentId]
                if docid:
                    if docid != documentId:
                        raise MambuPyError(
                            "Document with name '{}' does not has id '{}'".format(
                                documentName, documentId
                            )
                        )
                else:
                    docid = documentId
            except KeyError:
                raise MambuPyError(
                    "Document id '{}' is not an attachment of {}".format(
                        documentId, repr(self)
                    )
                )

        self._connector.mambu_delete_document(docid)
        self._attachments.pop(docid)


class MambuEntityCommentable(MambuStruct, MambuCommentable):
    """A Mambu object with commenting capabilities."""

    _comments = []
    """list of comments of an entity"""

    def get_comments(self, offset=None, limit=None, paginationDetails="OFF"):
        """Gets comments for this entity

        _comments list is cleaned and set with retrieved comments

        Args:
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination

        Returns:
          Mambu's response with retrieved comments
        """
        self._comments = []
        response = self._connector.mambu_get_comments(
            owner_id=self.id,
            owner_type=self._ownerType,
            offset=offset,
            limit=limit,
            paginationDetails=paginationDetails,
        )

        comments_list = json.loads(response.decode())

        for comment in comments_list:
            comm = MambuComment(**comment)
            self._comments.append(comm)

        return comments_list

    def comment(self, comment):
        """Comments this entity

        _comments list gets a new entry with comment.

        Args:
          comment (str): the text of the comment

        Returns:
          Mambu's response with metadata of the posted comment
        """
        response = self._connector.mambu_comment(
            owner_id=self.id, owner_type=self._ownerType, text=comment
        )

        comment = MambuComment(**dict(json.loads(response.decode())))
        self._comments.insert(0, comment)

        return response


class MambuEntityCF(MambuValueObject):
    """A Mambu CustomField obtained via an Entity.

    This is NOT a CustomField obtained through it's own endpoint, those go in
    another separate class.

    Here you just have a class to manage custom field values living inside some
    Mambu entity.
    """

    def __init__(self, value, path="", typecf="STANDARD", mcf=None):
        if typecf not in ["STANDARD", "GROUPED"]:
            raise MambuPyError("invalid CustomField type!")
        self._attrs = {"value": value, "path": path, "type": typecf, "mcf": mcf}
        self._cf_class = GenericClass

    def get_mcf(self):
        """Instance the MambuCustomField (MCF) of this entityCF.

        The MCF is set in the mcf property of this object.

        If this entityCF is a list, the mcf is set to a dictionary of
        field-MCFields.
        """
        mcf_mod = import_module("MambuPy.api.mambucustomfield")
        if self.mcf:
            return
        if isinstance(self.value, list) and len(self.value) > 0:
            self.mcf = {}
            for item in self.value:
                self.mcf["_index"] = None
                for key in [
                    k for k in item.keys() if k not in self.mcf and k != "_index"
                ]:
                    try:
                        self.mcf[key] = mcf_mod.MambuCustomField.get(key)
                    except MambuError:
                        self.mcf[key] = None
            return
        self.mcf = mcf_mod.MambuCustomField.get(self.path.split("/")[-1])


class MambuInstallment(MambuStruct):
    """Loan Account Installment (aka Repayment)"""

    def __repr__(self):
        """repr tells the class name, the number, the state and the dueDate"""
        return self.__class__.__name__ + " - #{}, {}, {}".format(
            self._attrs["number"],
            self._attrs["state"],
            self._attrs["dueDate"].strftime("%Y-%m-%d"),
        )


class MambuEntityOwnable(MambuStruct, MambuOwnable):
    """An entity which allows to be 'owned' by another.

    An owned entity has an 'accountHolderKey' and 'accountHolderType'
    fields.

    Because of that, you may call get_accountHolder on the owned
    entity to instantiate the MambuEntity who owns it.
    """

    def _assignEntObjs(
        self, entities=None, detailsLevel="BASIC", get_entities=False, debug=False
    ):
        """Overwrites `MambuPy.api.mambustruct._assignEntObjs` for MambuLoan

        Determines the type of account holder and instantiates accordingly
        """
        if entities is None:
            entities = self._entities

        try:
            accountholder_index = entities.index(
                ("accountHolderKey", "", "accountHolder")
            )
        except ValueError:
            accountholder_index = None

        if accountholder_index is not None and self.has_key("accountHolderKey"):
            if self.accountHolderType == "CLIENT":
                entities[accountholder_index] = (
                    "accountHolderKey",
                    "mambuclient.MambuClient",
                    "accountHolder",
                )
            elif self.accountHolderType == "GROUP":
                entities[accountholder_index] = (
                    "accountHolderKey",
                    "mambugroup.MambuGroup",
                    "accountHolder",
                )

        return super()._assignEntObjs(
            entities, detailsLevel=detailsLevel, get_entities=get_entities, debug=debug
        )
