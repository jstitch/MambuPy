"""Basic Struct for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy
from datetime import datetime
from importlib import import_module

from .classes import MambuMapObj
from ..mambuutil import MambuPyError, dateFormat


class MambuStruct(MambuMapObj):
    """Basic Struct for Mambu Objects with basic connection functionality."""

    _attrs = {}
    """Properties of the Mambu object"""

    _tzattrs = {}
    """TimeZones info:

        `_convertDict2Attrs` loses TZ info on datetime fields.

        We will save them on `_tzattrs` field. Prefering this method since this
        allows comparison with datetimes on your code without needing TZ
        initialized.

        For example:

        >>> today = datetime.now()
        >>> loan.creationDate < today

        That code works since now() doesn't have any TZ info.

        If creationDate has TZ info in it, you could not make the comparison.

        So, we need to preserve the TZ info somewhere else.

        Since TZ info is NOT the same for ALL the Mambu instance (each datetime
        may have different TZs due to daylight saving time differences for
        example), _tzattrs will hold the TZ for each datetime field.

        Only-date fields are also included but they lack TZ info by definition,
        so those fileds get a None TZ info.
    """

    _vos = []
    """List of Value Objects in the struct's _attrs.

       Each element must be a 2-tuple:
           ("name_in_attrs", "vos.class to instantiate")

       `_extractVOs` loops this list to instantiate the corresponding Value
       Objects inside _attrs. If the element in _attrs happens to be a list,
       the result will be a list of instantiated Value Objects

       `_updateVOs` loops this list to update the corresponding data in _attrs
    """

    _entities = []
    """List of Entities in the struct's _attrs.

    Each element must be a 3-tuple:
        ("name_of_key_in_attrs",
         "module.class to instantiate",
         "name_of_obj_in_attrs")
    """

    def __getattribute__(self, name):
        """Object-like get attribute for MambuStructs.

           If the attribute is not present at the _attrs dict, tries to build a
           function that calls :py:meth:`getEntities`, which in turns will try
           to instantiate an entity according to the requested attribute name
        """
        try:
            return super().__getattribute__(name)
        except AttributeError as attr:
            if name[0:4] == "get_" and len(name) > 4:
                ent = name[4:]
                return lambda **kwargs: self.getEntities([ent], **kwargs)
            else:
                raise attr

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
                    loan = []
                    for num, (e, te) in enumerate(zip(it, tzdata)):
                        d = convert(e, te)
                        if type(d) not in [dict, list, datetime]:
                            tzdata[num] = None
                        elif isinstance(d, datetime):
                            tzdata[num] = datetime.fromisoformat(tzdata[num]).tzname()
                        loan.append(d)
                    data = loan
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
                    if tzdata:  # no tzdata means a date (no time) object
                        data_asdate += tzdata[-6:]
                    else:
                        data_asdate = data_asdate[:10]
                    return data_asdate
                if data in [True, False]:
                    return str(data).lower()
                return str(data)

            if type(it) == type(iter([])):
                loan = []
                if tzdata:
                    for (e, te) in zip(it, tzdata):
                        loan.append(convert(e, te))
                else:
                    for e in it:
                        loan.append(convert(e))
                return loan
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
        on the root of the attrs argument.

        Args:
          attrs (dict): dictionary of fields from where customfields will be
                        extracted. If None, `self._attrs` will be used
        """

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
        with the corresponding property at the root of the `_attrs` dict, then
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

    def _extractVOs(self, get_entities=False, debug=False):
        """Loops _vos list to instantiate the corresponding Value Objects

           If the element in _attrs happens to be a list, the result will be a
           list of instantiated Value Objects.

           End result, the key with the name of the element will be replaced
           with the instantiated Value Object. And the original element will
           change its key name from 'elem' to 'vo_elem'.

           Args:
             get_entities (bool): should MambuPy automatically instantiate
                                  other MambuPy entities found inside the Value
                                  Objects?
             debug (bool): print debugging info
        """
        vos_module = import_module(".vos", "mambupy.api")
        for elem, voclass in self._vos:
            try:
                vo_data = self._attrs[elem]
            except KeyError:
                continue
            if isinstance(vo_data, list):
                vo_obj = []
                already = False
                for item in vo_data:
                    if isinstance(item, getattr(vos_module, voclass)):
                        already = True
                        continue
                    vo_item = getattr(vos_module, voclass)(**item)
                    vo_item._extractVOs()
                    if get_entities:
                        vo_item._assignEntObjs(
                            vo_item._entities,
                            get_entities=get_entities,
                            debug=debug)
                    vo_obj.append(vo_item)
                if already:
                    continue
            else:
                if isinstance(vo_data, getattr(vos_module, voclass)):
                    continue
                vo_obj = getattr(vos_module, voclass)(**vo_data)
                vo_obj._extractVOs()
                if get_entities:
                    vo_obj._assignEntObjs(
                        vo_obj._entities,
                        get_entities=get_entities,
                        debug=debug)
            self._attrs[elem] = vo_obj

    def _updateVOs(self):
        """Loops _vos list to update the corresponding data in _attrs

           End result, the element with the original element in _attr will have
           its data updated, the Value Object will dissappear and the key name
           of the original element will return to be from 'vo_elem' to 'elem'
        """
        vos_module = import_module(".vos", "mambupy.api")
        for elem, voclass in self._vos:
            try:
                vo_obj = self._attrs[elem]
            except KeyError:
                continue
            if isinstance(vo_obj, list):
                vo_data = []
                already = False
                for item in vo_obj:
                    if not isinstance(item, getattr(vos_module, voclass)):
                        already = True
                        continue
                    item._updateVOs()
                    vo_item = copy.deepcopy(item._attrs)
                    vo_data.append(vo_item)
                if already:
                    continue
            else:
                if not isinstance(vo_obj, getattr(vos_module, voclass)):
                    continue
                vo_obj._updateVOs()
                vo_data = copy.deepcopy(vo_obj._attrs)
            self._attrs[elem] = vo_data

    def getEntities(
        self,
        entities,
        detailsLevel="BASIC",
        get_entities=False,
        debug=False
    ):
        """Retrieve certain entities from the properties of this MambuEntity.

           Args:
             entities (list): list of strings with the name of the entity to
                              retrieve
             detailsLevel (str): "BASIC" or "FULL" for the retrieved entities
             get_entities (bool): should MambuPy automatically instantiate
                                  other MambuPy entities found inside the
                                  retrieved entities?
             debug (bool): print debugging info
        """
        ents = []  # do not be hasty, that is my motto
        for entity in entities:
            entwife = [enti for enti in self._entities if enti[2] == entity]
            if len(entwife) == 0:  # you see, we lost the entwives
                if (
                    entity in self._attrs and
                    isinstance(self._attrs[entity], list)
                ):  # let the ents undertake the quest to look for the entwives!
                    for entling in self._attrs[entity]:
                        if isinstance(entling, MambuStruct):
                            entling._assignEntObjs(
                                entities=entling._entities,
                                detailsLevel=detailsLevel,
                                get_entities=get_entities,
                                debug=debug)
                else:
                    raise MambuPyError(
                        "The name {} is not part of the nested entities".format(
                            entity))
            else:  # come back to me and say my land is best!
                ents.extend(entwife)

        if len(ents) > 0:
            self._assignEntObjs(
                entities=ents,
                detailsLevel=detailsLevel,
                get_entities=get_entities,
                debug=debug)

    def _assignEntObjs(
        self,
        entities=None,
        detailsLevel="BASIC",
        get_entities=False,
        debug=False
    ):
        """Loops entities list of tuples to instantiate MambuPy entities from Mambu.

           End result: new properties will appear on the MambuPy object other
           :py:obj:`MambuPy.api.entities.MambuEntity` objects retrieved from Mambu

           Args:
             entities (list): list of tuples with information of the entity and
                              property to instantiate. Look at
                              :py:obj:`MambuPy.api.mambustruct.MambuStruct._entities`
             detailsLevel (str): "BASIC" or "FULL" for the retrieved entities
             get_entities (bool): should MambuPy automatically instantiate
                                  other MambuPy entities found inside the
                                  retrieved entities?
             debug (bool): print debugging info
        """
        def instance_entity_obj(encoded_key, ent_mod, ent_class, **kwargs):
            """Instantiates a single MambuPy object calling its get method.

               If the object doesn't supports detailsLevel (MambuProduct),
               omit it.

               Args:
                 encoded_key (str): encoded key of the entity to retrieve
                                    from Mambu
                 ent_mod (obj): module holding the class to instantiate
                 ent_class (str): class to instantiate
                 kwargs (dict): extra parameters for the get method

               Returns:
                 MambuPyObject (obj): instantiation of the object from Mambu
            """
            try:
                try:
                    return getattr(ent_mod, ent_class).get(encoded_key, **kwargs)
                except TypeError:
                    kwargs.pop("detailsLevel")
                    return getattr(ent_mod, ent_class).get(encoded_key, **kwargs)
            except AttributeError:
                return

        if entities is None:
            entities = self._entities

        for encodedKey, ent_path, new_property in entities:
            ent_module = ".".join(ent_path.split(".")[:-1])
            ent_class = ent_path.split(".")[-1]
            ent_mod = import_module("." + ent_module, "mambupy.api")

            try:
                enc_key = self._attrs[encodedKey]
            except KeyError:
                continue

            if isinstance(enc_key, list):
                ent_item = []
                for item in enc_key:
                    ent_item.append(
                        instance_entity_obj(
                            item, ent_mod, ent_class,
                            detailsLevel=detailsLevel,
                            get_entities=get_entities,
                            debug=debug))
            else:
                ent_item = instance_entity_obj(
                    enc_key, ent_mod, ent_class,
                    detailsLevel=detailsLevel,
                    get_entities=get_entities,
                    debug=debug)

            self[new_property] = ent_item
