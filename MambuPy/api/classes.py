"""Base and utility Classes for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy


class GenericClass:  # pragma: no coverage
    """Generic class for init of MambuMapObj"""

    def __init__(self, *args, **kwargs):
        pass


class MambuMapObj:
    """An object with dictionary-like behaviour for key-value data"""

    def __init__(self, cf_class=GenericClass, **kwargs):
        self._attrs = {}
        self._cf_class = cf_class
        if hasattr(self, "_default_tzattrs"):
            self._tzattrs = copy.deepcopy(self._default_tzattrs)
        else:
            self._tzattrs = {}
        if "tzattrs" in kwargs:
            self._tzattrs.update(copy.deepcopy(kwargs.pop("tzattrs")))
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
            if isinstance(_attrs, list) or name not in _attrs:
                # magic won't happen when not a dict-like MambuMapObj or
                # when _attrs has not the 'name' key (this last one means
                # that if 'name' is not a property of the object too,
                # AttributeError will raise by default)
                return object.__getattribute__(self, name)
            # all else, read the property from the _attrs dict, but with a . syntax
            # if a cf_class, just return its value
            if _attrs[name].__class__.__name__ == self._cf_class.__name__:
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
                if isinstance(_attrs, list):
                    # when not treating with a dict-like MambuMapObj...
                    raise AttributeError
                try:
                    # see if 'name' is currently a property of the object
                    object.__getattribute__(self, name)
                except AttributeError:
                    # if not, then assign it as a new key in the dict
                    if (
                        name in _attrs
                        and _attrs[name].__class__.__name__ == self._cf_class.__name__
                    ):
                        path = _attrs[name]["path"]
                        typecf = _attrs[name]["type"]
                        _attrs[name] = self._cf_class(value, path, typecf)
                    else:
                        _attrs[name] = value
                else:  # pragma: no cover
                    raise AttributeError
            except AttributeError:
                # all else assign it as a property of the object
                object.__setattr__(self, name, value)

    def __getitem__(self, key):
        """Dict-like key query"""
        # if a cf_class, just return its value
        if self._attrs[key].__class__.__name__ == self._cf_class.__name__:
            return self._attrs[key]["value"]
        return self._attrs[key]

    def __setitem__(self, key, value):
        """Dict-like set"""
        # if no _attrs attribute, should be automatically created?
        if (
            key in self._attrs
            and self._attrs[key].__class__.__name__ == self._cf_class.__name__
        ):
            path = self._attrs[key]["path"]
            typecf = self._attrs[key]["type"]
            self._attrs[key] = self._cf_class(value, path, typecf)
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
        if isinstance(self._attrs, dict):
            return self._attrs.get(key, default)
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
            if isinstance(self._attrs, dict):
                return key in self._attrs
            raise AttributeError  # if _attrs is not a dict
        except AttributeError:  # if _attrs doesnt exist
            raise NotImplementedError
