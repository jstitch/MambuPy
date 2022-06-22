from base64 import b64decode
import importlib
import os

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
                obj = _class2(urlfunc=None, fullDetails=self.fullDetails)
                obj._entid = entity.id
                obj.wrapped2 = entity
                obj.mambuclassname = self.mambuclassname
                obj.mambuclass1 = self.mambuclass1
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
                    _class_base = import_class("MambuPy.rest", self.mambuclassname)
                    _class = self.mambuclass1
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self._entid,
                        mambuclassname=self.mambuclassname,
                        mambuclass1=_class_base)
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
                    _class_base = import_class("MambuPy.rest", self.mambuclassname)
                    _class = self.mambuclass1
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self._entid,
                        mambuclassname=self.mambuclassname,
                        mambuclass1=_class_base)
                    self.wrapped1.preprocess()
                    self.wrapped1.postprocess()
                attribute = getattr(self.wrapped1, name)
                return attribute

    def __setattr__(self, name, value):
        if name not in [
                "_class", "_entid",
                "wrapped1", "wrapped2",
                "mambuclassname", "mambuclass1",
                "fullDetails", "detailsLevel"]:
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
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - id: %s" % self.id
        except KeyError:
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - " + str(self.attrs)
        except AttributeError:
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - len: %s" % len(self.wrapped2)
        except TypeError:
            return self.mambuclass1.__name__ + " - len: %s" % len(self.wrapped2)

    def __len__(self):
        return self.wrapped2.__len__()

    def update(self, data, *args, **kwargs):
        fields = []
        for ci in data.get("customInformation", {}):
            self[ci["customFieldID"]] = ci["value"]
            fields.append(ci["customFieldID"])
        self.wrapped2.patch(fields=fields)

        return 1

    def update_patch(self, data, *args, **kwargs):
        fields = []
        for k, v in data.items():
            self[k] = v
            fields.append(k)
        self.wrapped2.patch(fields=fields)

        return 1

    def upload_document(self, data, *args, **kwargs):
        fname = "/tmp/_mamburest1to2_{}.{}".format(
            data["document"]["name"], data["document"]["type"])
        with open(fname, "wb") as f:
            f.write(b64decode(
                data["documentContent"][1:-1]))
        self.wrapped2.attach_document(
            fname,
            title=data["document"]["name"],
            notes="uploaded via rest1to2 adapter")
        os.remove(fname)

        return 1
