""""""

import json

from .mambuconnector import MambuConnectorREST

class MambuStruct():
    """"""

    _connector = MambuConnectorREST()
    """"""

    def __getitem__(self, key):
        """Dict-like key query"""
        return self.attrs[key]

    def __setitem__(self, key, value):
        """Dict-like set"""
        # if no attrs attribute, should be automatically created?
        self.attrs[key] = value

    def __delitem__(self, key):
        """Dict-like del key"""
        del self.attrs[key]

    def __hash__(self):
        """Hash of the object"""
        try:
            return hash(self.encodedKey)
        except AttributeError:
            try:
                return hash(self.__class__.__name__ + self.id)
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

    def values(self):
        """Dict-like behaviour"""
        try:
            return self.attrs.values()
        except AttributeError:
            raise NotImplementedError

    def connect(self, entid):
        """"""
        self.resp = self._connector.mambu_get(
            entid, url_prefix=self._url_prefix)

        self.attrs = dict(json.loads(self.resp.decode()))
