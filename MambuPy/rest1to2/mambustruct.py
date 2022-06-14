import importlib

from mambupy.rest.mambustruct import MambuStruct as MambuStruct1


def process_filters(filters, kwargs):
    for _filter in filters:
        if _filter in kwargs:
            if "filters" not in kwargs:
                kwargs["filters"] = {}
            filt = kwargs.pop(_filter)
            kwargs["filters"][_filter] = filt


def import_class(path, _object):
    if type(_object) == str:
        mod_str = _object
    else:
        mod_str = _object.__class__.__name__
    module = importlib.import_module(path + "." + mod_str.lower())
    _class = getattr(module, mod_str)

    return _class


class MambuStruct(MambuStruct1):
    attrs = {}

    def __init__(self, *args, **kwargs):
        self.wrapped1 = None
        self.wrapped2 = None
        if "connect" in kwargs:
            kwargs.pop("connect")
        if "fullDetails" in kwargs:
            fullDetails = kwargs.pop("fullDetails")
            detailsLevel = "FULL" if fullDetails else "BASIC"
            object.__setattr__(self, "fullDetails", fullDetails)
            object.__setattr__(self, "detailsLevel", detailsLevel)
        else:
            object.__setattr__(self, "fullDetails", False)
            object.__setattr__(self, "detailsLevel", "BASIC")

        if "mambuclassname" in kwargs:
            self.mambuclassname = kwargs.pop("mambuclassname")
        else:
            self.mambuclassname = self.__class__.__name__
        if "mambuclass1" in kwargs:
            self.mambuclass1 = kwargs.pop("mambuclass1")
        else:
            self.mambuclass1 = import_class(
                "MambuPy.rest", self.__class__.__name__)
        _class = import_class("MambuPy.api", self.mambuclassname)

        if "urlfunc" in kwargs and kwargs["urlfunc"] is None:
            self.wrapped2 = _class()
            return

        if "entid" in kwargs:
            self._entid = kwargs["entid"]
            self.wrapped2 = _class.get(
                detailsLevel=self.detailsLevel, *args, **kwargs)
        else:
            self._entid = ""
            entities = _class.get_all(
                detailsLevel=self.detailsLevel, *args, **kwargs)
            self.wrapped2 = []
            _class2 = import_class("MambuPy.rest1to2", self.mambuclassname)
            for entity in entities:
                obj = _class2(urlfunc=None)
                obj._entid = entity.id
                obj.wrapped2 = entity
                obj.mambuclassname = self.mambuclassname
                obj.mambuclass1 = self.mambuclass1
                obj.wrapped1 = obj.mambuclass1(
                    entid=obj._entid,
                    fullDetails=self.fullDetails,
                    *args, **kwargs)
                self.wrapped2.append(obj)

    def __getitem__(self, key):
        try:
            item = super().__getitem__(key)
            return item
        except KeyError:
            try:
                item = self.wrapped2[key]
                return item
            except (KeyError, TypeError):
                if not self.wrapped1 and self._entid != "":
                    _class = import_class("MambuPy.rest", self.mambuclassname)
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self._entid,
                        mambuclassname=self.mambuclassname,
                        mambuclass1=super().__class__)
                    self.wrapped1.preprocess()
                    self.wrapped1.postprocess()
                item = self.wrapped1[key]
                return item

    def __setitem__(self, key, value):
        try:
            self.wrapped2[key] = value
        except TypeError:
            self.wrapped1[key] = value

    def __getattribute__(self, name):
        try:
            attribute = super().__getattribute__(name)
            return attribute
        except AttributeError:
            try:
                attribute = getattr(self.wrapped2, name)
                return attribute
            except AttributeError:
                if not self.wrapped1 and self._entid != "":
                    _class = import_class("MambuPy.rest", self.mambuclassname)
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self._entid,
                        mambuclassname=self.mambuclassname,
                        mambuclass1=super().__class__)
                    self.wrapped1.preprocess()
                    self.wrapped1.postprocess()
                attribute = getattr(self.wrapped1, name)
                return attribute

    def __setattr__(self, name, value):
        if name not in [
                "_class", "_entid",
                "wrapped1", "wrapped2",
                "mambuclassname", "mambuclass1"]:
            try:
                self.wrapped2.__setattr__(name, value)
            except AttributeError:
                self.wrapped1.__setattr__(name, value)
        else:
            object.__setattr__(self, name, value)

    def haskey(self, key):
        try:
            return self.wrapped2.has_key(key)
        except AttributeError:
            return self.wrapped1.has_key(key)

    def __str__(self):
        return self.wrapped2.__str__()

    def __repr__(self):
        try:
            return self.wrapped1.__class__.__name__ + " - id: %s" % self.id
        except KeyError:
            return self.wrapped1.__class__.__name__ + " - " + str(self.attrs)
        except AttributeError:
            return self.__class__.__name__ + " - len: %s" % len(self.wrapped2)
        except TypeError:
            return self.mambuclass1.__class__.__name__ + " - len: %s" % len(self.wrapped2)

    def __len__(self):
        return self.wrapped2.__len__()
