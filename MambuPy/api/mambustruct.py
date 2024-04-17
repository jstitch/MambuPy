"""Basic Struct for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy
from datetime import datetime
from importlib import import_module

from .classes import MambuMapObj
from ..mambuutil import MambuPyError, date_format


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
        ("name_of_key_in_attrs", # element in attrs to obtain the key
         "module.class to instantiate", # class to instantiate for the given key
         "name_of_obj_in_attrs") # where in attrs to update with instantiated obj
    """

    def __getattribute_for_one_cf(self, ent, value, mcf):
        if mcf and isinstance(value, str) and "_LINK" in mcf.type:
            link_type = mcf.type[:-5]
            package = "mambu" + link_type.lower()
            classname = "Mambu" + link_type.capitalize()
            classpath = package + "." + classname

            return lambda **kwargs: self.getEntities(
                [ent], config_entities=[(ent, classpath, ent)], **kwargs
            )[0]

        return lambda **kwargs: value

    def __getattribute_for_loop(self, ent, value, mcf):
        attributes = []
        for ind, item in enumerate(value):
            values = {}
            for key, val in item.items():
                values[key] = self.__getattribute_for_one_cf(
                    ent + "/" + str(ind) + "/" + key, val, mcf[key]
                )()
            attributes.append(values)
        return lambda **kwargs: attributes

    def __getattribute_for_cf(self, ent, entity):
        if isinstance(entity.value, list):
            return self.__getattribute_for_loop(ent, entity.value, entity.mcf)
        return self.__getattribute_for_one_cf(ent, entity.value, entity.mcf)

    def __getattribute__(self, name):
        """Object-like get attribute for MambuStructs.

        If the attribute is not present at the _attrs dict, tries to build a
        function that calls :py:meth:`getEntities`, which in turns will try
        to instantiate an entity according to the requested attribute name
        """
        try:
            return super().__getattribute__(name)
        except AttributeError as attr_err:
            if name[0:4] == "get_" and len(name) > 4:
                ent = name[4:]
                if ent in self._attrs.keys():
                    entity = self._attrs[ent]
                    if entity.__class__.__name__ == self._cf_class.__name__:
                        entity.get_mcf()
                        return self.__getattribute_for_cf(ent, entity)
                    return lambda **kwargs: entity
                return lambda **kwargs: self.getEntities([ent], **kwargs)[0]
            else:
                raise attr_err

    def __convert_from_dict_to_basic_types_non_constant_fields(
        self, k, data_dict, data, tzdata
    ):
        try:
            data_dict[k] = self.__convert_to_basic_types(data[k], tzdata[k])
            if type(data_dict[k]) not in [dict, list, datetime]:
                del tzdata[k]
            elif isinstance(data_dict[k], datetime):
                tzdata[k] = datetime.fromisoformat(tzdata[k]).tzname()
        except (KeyError, ValueError, TypeError):
            data_dict[k] = self.__convert_to_basic_types(data[k])

    def __convert_from_dict_to_basic_types(self, it_dict, data, tzdata, constantFields):
        data_dict = {}
        for k in it_dict:
            if k in constantFields or (len(k) > 2 and k[-3:] == "Key"):
                data_dict[k] = data[k]
                if tzdata and k in tzdata:
                    del tzdata[k]
            else:
                self.__convert_from_dict_to_basic_types_non_constant_fields(
                    k, data_dict, data, tzdata
                )
        return data_dict

    def __convert_from_list_to_basic_types(self, it_list, data, tzdata, constantFields):
        data_list = []
        for num, (e, te) in enumerate(zip(it_list, tzdata)):
            d = self.__convert_to_basic_types(e, te)
            if type(d) not in [dict, list, datetime]:
                tzdata[num] = None
            elif isinstance(d, datetime):
                tzdata[num] = datetime.fromisoformat(tzdata[num]).tzname()
            data_list.append(d)
        return data_list

    def __convert_to_basic_types_base_cases(self, data):
        if data in ["TRUE", "true", "FALSE", "false"]:
            return data.lower() == "true"
        try:
            i_data = int(data)
            if (
                str(i_data) != data
            ):  # if string has trailing 0's, leave it as string, to not lose them
                return data
            return i_data
        except (TypeError, ValueError):
            try:
                f_data = float(data)
                return f_data
            except (TypeError, ValueError):
                try:
                    return date_format(data)
                except (TypeError, ValueError):
                    return data

        return data

    def __convert_to_basic_types(self, data, tzdata=None, constantFields=None):
        """Recursively convert the fields on the data given to a python
        object.

        If data is iterable, iterates its elements and try to convert them.

        If data is a string, tries to convert its value to a basic data type:

        Basic data types supported:
          - int: an int number
          - float: a floating point number
          - datetime: if the string holds a valid datetime in a date_format
                      specific format

        A list of fields that should stay as-they-come (strings) is supported.
        All fields whose name ends with "Key" is also ignored.

        Args:
          data (obj): an object whose value should be converted to a basic
                      type
          tzdata (obj): mirror of data, holding only the TZ data for datetimes.
          constantFields (list): fields that will be ignored for conversion
        """
        if not constantFields:
            constantFields = []
        # Iterators, lists and dictionaries
        # Here comes the recursive calls!
        try:
            it = data
            if isinstance(it, dict):
                data = self.__convert_from_dict_to_basic_types(
                    it, data, tzdata, constantFields
                )
            if isinstance(it, list):
                data = self.__convert_from_list_to_basic_types(
                    it, data, tzdata, constantFields
                )
        except TypeError:
            pass
        except Exception as ex:  # pragma: no cover
            # unknown exception
            raise ex

        # Base case!
        return self.__convert_to_basic_types_base_cases(data)

    def _convertDict2Attrs(self, *args, **kwargs):
        """Each element on the attrs attribute gets converted to a
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

        self._attrs = self.__convert_to_basic_types(
            self._attrs, self._tzattrs, constantFields
        )

    def __convert_from_dict_basic_types_to_str(self, it_dict, data, tzdata):
        d = {}
        for k in it_dict:
            if tzdata and k in tzdata:
                d[k] = self.__convert_basic_types_to_str(data[k], tzdata[k])
            else:
                d[k] = self.__convert_basic_types_to_str(data[k])
        return d

    def __convert_from_list_basic_types_to_str(self, it_list, data, tzdata):
        data_list = []
        if tzdata:
            for e, te in zip(it_list, tzdata):
                data_list.append(self.__convert_basic_types_to_str(e, te))
        else:
            for e in it_list:
                data_list.append(self.__convert_basic_types_to_str(e))
        return data_list

    def __convert_basic_types_to_str_base_cases(self, data, tzdata):
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

    def __convert_basic_types_to_str(self, data, tzdata=None):
        """Recursively convert the fields on the data given to strings.

        Datetime objects are converted to ISO format, adding TZ info if
        available on tzdata.

        Skips every MambuMapObj owned by this entity.

        If the object is an iterable one, it goes down to each of its
        elements and turns its attributes too

        The base case is when it's a MambuMapObj class (this one) so it
        just 'serializes' the attr atribute.

        Args:
          data (obj): an object whose value should be converted to string.
          tzdata (obj): mirror of data, holding only the TZ data for datetimes.
        """
        # Base case!
        if isinstance(data, MambuMapObj):
            data._serializeFields()
            return data
        try:
            it = iter(data)
        except TypeError:
            return self.__convert_basic_types_to_str_base_cases(data, tzdata)

        # Recursive calls
        if isinstance(data, list):
            return self.__convert_from_list_basic_types_to_str(it, data, tzdata)
        elif isinstance(data, dict):
            return self.__convert_from_dict_basic_types_to_str(it, data, tzdata)
        # elif ... tuples? sets?
        return data

    def _serializeFields(self, *args, **kwargs):
        """Every attribute of the Mambu object is turned in to a string
        representation.

        Args:
          data (obj): an object whose value should be converted to string.
          tzdata (obj): mirror of data, holding only the TZ data for datetimes.
        """
        self._attrs = self.__convert_basic_types_to_str(self._attrs, self._tzattrs)

    def __extract_customfields_from_dict(self, val_dict, attr, attrs):
        for key, value in val_dict.items():
            attrs[key] = self._cf_class(value, "/{}/{}".format(attr, key), "STANDARD")

    def __extract_customfields_from_list(self, val_list, attr, attrs):
        attrs[attr[1:]] = self._cf_class(
            copy.deepcopy(val_list), "/{}".format(attr), "GROUPED"
        )
        for ind, value in enumerate(val_list):
            if isinstance(value, dict):
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
                    "CustomFieldSet {} is not a list of dictionaries!".format(attr)
                )

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
            if isinstance(val, dict):
                self.__extract_customfields_from_dict(val, attr, attrs)
            elif isinstance(val, list):
                self.__extract_customfields_from_list(val, attr, attrs)
            else:
                raise MambuPyError("CustomFieldSet {} is not a dictionary!".format(attr))

    def __get_value_or_ek(self, obj):
        if isinstance(obj, MambuStruct):
            return obj.encodedKey
        return obj

    def __update_customfields_from_dict(self, val_dict, attr, cfs):
        for key in val_dict.keys():
            try:
                if self[key] in [True, False]:
                    self[key] = str(self[key]).upper()
                self._attrs[attr][key] = self.__get_value_or_ek(self[key])
                cfs.append(key)
            except KeyError:
                pass

    def __update_customfields_from_list(self, val_list, attr, cfs):
        for ind, value in [
            (ind, value) for ind, value in enumerate(val_list) if isinstance(value, dict)
        ]:
            for key in [k for k in value.keys() if k[0] != "_"]:
                try:
                    if self[key + "_" + str(ind)] in [True, False]:
                        self[key + "_" + str(ind)] = str(
                            self[key + "_" + str(ind)]
                        ).upper()
                    if self[attr][ind][key] != self[key + "_" + str(ind)]:
                        self[attr[1:]][ind][key] = self.__get_value_or_ek(
                            self[key + "_" + str(ind)]
                        )
                    cfs.append(key + "_" + str(ind))
                except KeyError:
                    pass
        try:
            self._attrs[attr] = copy.deepcopy(self[attr[1:]])
            cfs.append(attr[1:])
        except KeyError:
            pass

    def _updateCustomFields(self):
        """Loops through every custom field set and update custom field values
        with the corresponding property at the root of the `_attrs` dict, then
        deletes the property at root"""
        cfs = []
        # updates customfieldsets
        for attr, val in [
            atr
            for atr in self._attrs.items()
            if atr[0][0] == "_"
            and atr[0][1:] not in [ent_config[2] for ent_config in self._entities]
        ]:
            if isinstance(val, dict):
                self.__update_customfields_from_dict(val, attr, cfs)
            elif isinstance(val, list):
                self.__update_customfields_from_list(val, attr, cfs)
            else:
                raise MambuPyError(
                    "CustomFieldSet {} is not a dictionary or list of dictionaries!".format(
                        attr
                    )
                )
        # deletes _attrs root keys of custom fields
        for field in cfs:
            del self._attrs[field]

    def __extract_vos_from_list(
        self, vo_data, vos_module, voclass, elem, get_entities=False, debug=False
    ):
        """Extracts the VOs from a list.

        Given a list of data representing a VO, extract and instantiate each of
        them.

        Args:
          vo_data (list): list of VOs to extract
          vos_module (module): VOs module from MambuPy
          voclass (class): class of the VOs to instantiate
          elem (obj): elem at attrs where the list comes from
          get_entities (bool): should MambuPy automatically instantiate other
                               MambuPy entities found inside the Value Objects?
          debug (bool): print debugging info

        Returns:
          (vo_obj, already) (tuple): (vo obj, bool) a list of instances of VOs
                                     and if it has already been instantiated
                                     (bool)
        """
        vo_obj = []
        already = False
        for ind, item in enumerate(vo_data):
            if isinstance(item, getattr(vos_module, voclass)):
                already = True
                continue
            vo_item = getattr(vos_module, voclass)(**item)
            vo_item._tzattrs = self._tzattrs[elem][ind]
            vo_item._extractVOs()
            if get_entities:
                vo_item._assignEntObjs(
                    vo_item._entities, get_entities=get_entities, debug=debug
                )
            vo_obj.append(vo_item)

        return vo_obj, already

    def _extractVOs(self, get_entities=False, debug=False):
        """Loops _vos list to instantiate the corresponding Value Objects.

        If the element in _attrs happens to be a list, the result will be a
        list of instantiated Value Objects.

        End result, the key with the name of the element will be replaced with
        the instantiated Value Object. And the original element will change its
        key name from 'elem' to 'vo_elem'.

        Args:
          get_entities (bool): should MambuPy automatically instantiate other
                               MambuPy entities found inside the Value Objects?
          debug (bool): print debugging info
        """
        vos_module = import_module(".vos", "mambupy.api")
        for elem, voclass in self._vos:
            try:
                vo_data = self._attrs[elem]
            except KeyError:
                continue

            if isinstance(vo_data, list):
                vo_obj, already = self.__extract_vos_from_list(
                    vo_data, vos_module, voclass, elem, get_entities, debug
                )
                if already:
                    continue
            elif isinstance(vo_data, getattr(vos_module, voclass)):
                continue
            else:
                vo_obj = getattr(vos_module, voclass)(**vo_data)
                vo_obj._tzattrs = self._tzattrs[elem]
                vo_obj._extractVOs()
                if get_entities:
                    vo_obj._assignEntObjs(
                        vo_obj._entities, get_entities=get_entities, debug=debug
                    )

            self._attrs[elem] = vo_obj

    def __update_vos_from_list(self, vo_obj, vos_module, voclass):
        """Updates the VOs from a list.

        Given a list of VOs, updates each element's data to the attrs dict.

        Args:
          vo_obj (obj): the VO which data will be updated at the attrs dict.
          vos_module (module): VOs module from MambuPy
          voclass (class): class of the VOs to instantiate

        Returns:
          (vo_data, already) (tuple): (dict, bool) a list of updated data and
                                      if it has already been updated (bool)
        """
        vo_data = []
        already = False
        for item in vo_obj:
            if not isinstance(item, getattr(vos_module, voclass)):
                already = True
                continue
            item._updateVOs()
            vo_item = copy.deepcopy(item._attrs)
            vo_data.append(vo_item)

        return vo_data, already

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
                vo_data, already = self.__update_vos_from_list(
                    vo_obj, vos_module, voclass
                )
                if already:
                    continue
            elif not isinstance(vo_obj, getattr(vos_module, voclass)):
                continue
            else:
                vo_obj._updateVOs()
                vo_data = copy.deepcopy(vo_obj._attrs)
            self._attrs[elem] = vo_data

    def getEntities(
        self,
        entities,
        config_entities=None,
        detailsLevel="BASIC",
        get_entities=False,
        debug=False,
    ):
        """Retrieve certain entities from the properties of this MambuEntity.

        Args:
          entities (list): list of strings with the name of the entity to
                           retrieve
          config_entities (list of tuples): list of tuples with information
                                            of the entity and property to
                                            instantiate
                     :py:obj:`MambuPy.api.mambustruct.MambuStruct._entities`
          detailsLevel (str): "BASIC" or "FULL" for the retrieved entities
          get_entities (bool): should MambuPy automatically instantiate
                               other MambuPy entities found inside the
                               retrieved entities?
          debug (bool): print debugging info

        Returns:
          MambuPyObject (obj): instantiation of the object from Mambu
        """
        if not config_entities:
            config_entities = self._entities
        ents = []  # do not be hasty, that is my motto
        ent_kids = []
        for entity in entities:
            entwife = [enti for enti in config_entities if enti[2] == entity]
            if len(entwife) == 0:  # you see, we lost the entwives
                if entity in self._attrs and isinstance(
                    self._attrs[entity], list
                ):  # let the ents undertake the quest to look for the entwives!
                    for entling in [
                        entkid
                        for entkid in self._attrs[entity]
                        if isinstance(entkid, MambuStruct)
                    ]:
                        ent_kids.append(
                            entling._assignEntObjs(
                                entities=entling._entities,
                                detailsLevel=detailsLevel,
                                get_entities=get_entities,
                                debug=debug,
                            )
                        )
                else:
                    raise MambuPyError(
                        "The name {} is not part of the nested entities".format(entity)
                    )
            else:  # come back to me and say my land is best!
                ents.extend(entwife)

        if len(ents) > 0:
            return self._assignEntObjs(
                entities=ents,
                detailsLevel=detailsLevel,
                get_entities=get_entities,
                debug=debug,
            )
        return ent_kids

    def __get_enc_key(self, proprty):
        """Gets a property from the obj, supposedly holding an encodedKey to
        return.

        Args:
          proprty (str): a property to get, supposedly an encodedKey.

        Returns:
          encodedKey (str) or None
        """
        try:
            enc_key = getattr(self, proprty)
            if not isinstance(enc_key, str) and not isinstance(enc_key, list):
                try:
                    enc_key = enc_key["encodedKey"]
                except KeyError:
                    enc_key = enc_key["id"]
        except AttributeError:
            try:
                prop, index, key = proprty.split("/")
                enc_key = getattr(self, prop)[int(index)][key]
            except ValueError:
                return None
        except KeyError:
            return None

        return enc_key

    def __instance_entity_obj(self, encoded_key, ent_mod, ent_class, **kwargs):
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

    def __assign_new_property(self, new_property, ent_item, default_prop_path):
        """Assigns the value ent_item to a new property in the obj.

        Args:
          new_property (str): a new property to be assigned in  the obj.
          ent_item (obj): the value to assign
          default_prop_path (str): a / divided string with the path of the
                                   property, in case that new_property doesn't
                                   exists originally in the obj
        """
        try:
            entity = self._attrs[new_property]
            if entity.__class__.__name__ == self._cf_class.__name__:
                self._attrs[new_property].value = ent_item
                try:
                    proprty, index, key = entity.path[2:].split("/")
                    getattr(self, proprty)[int(index)][key] = ent_item
                except ValueError:
                    pass
            self["_" + new_property] = entity
            self[new_property] = ent_item
        except KeyError:
            try:
                proprty, index, key = default_prop_path.split("/")
                getattr(self, proprty)[int(index)][key] = ent_item
                setattr(self, key + "_" + index, ent_item)
            except ValueError:
                self[new_property] = ent_item

    def _assignEntObjs(
        self, entities=None, detailsLevel="BASIC", get_entities=False, debug=False
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
        if entities is None:
            entities = self._entities

        instances = []
        for encodedKey, ent_path, new_property in entities:
            ent_module = ".".join(ent_path.split(".")[:-1])
            ent_class = ent_path.split(".")[-1]
            try:
                ent_mod = import_module("." + ent_module, "mambupy.api")
            except ModuleNotFoundError:
                ent_mod = import_module(ent_module)

            enc_key = self.__get_enc_key(encodedKey)
            if not enc_key:
                continue

            if isinstance(enc_key, list):
                ent_item = []
                for item in enc_key:
                    ent_item.append(
                        self.__instance_entity_obj(
                            item,
                            ent_mod,
                            ent_class,
                            detailsLevel=detailsLevel,
                            get_entities=get_entities,
                            debug=debug,
                        )
                    )
            else:
                ent_item = self.__instance_entity_obj(
                    enc_key,
                    ent_mod,
                    ent_class,
                    detailsLevel=detailsLevel,
                    get_entities=get_entities,
                    debug=debug,
                )

            self.__assign_new_property(new_property, ent_item, encodedKey)

            instances.append(ent_item)

        return instances
