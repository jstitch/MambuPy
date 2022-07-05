from base64 import b64decode
from copy import deepcopy
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
    DEFAULTS = {}
    attrs = {}

    def __init__(self, *args, **kwargs):
        self.wrapped1 = None
        self.wrapped2 = None
        connect = True
        if "connect" in kwargs:
            connect = kwargs.pop("connect")
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
        if "mambuclass2" in kwargs:
            self.mambuclass2 = kwargs.pop("mambuclass2")
        else:
            self.mambuclass2 = import_class(
                "mambupy.api", self.mambuclassname)

        self._entid = None
        self.__args = ()
        self.__kwargs = {}
        self.__args = deepcopy(args)
        for k, v in kwargs.items():
            self.__kwargs[k] = deepcopy(v)

        if "urlfunc" in self.__kwargs and self.__kwargs["urlfunc"] is None:
            self.wrapped2 = self.mambuclass2()
            return

        if connect:
            self.connect(*self.__args, **self.__kwargs)

    def __getitem__(self, key):
        try:
            item = self.wrapped2[key]
            return item
        except KeyError:
            try:
                item = super().__getitem__(key)
                return item
            except (KeyError, TypeError):
                try:
                    item = self.__getattribute__(key)
                    return item
                except AttributeError:
                    raise KeyError("{}".format(key))

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
                try:
                    return self.DEFAULTS[name]
                except KeyError:
                    if not self.wrapped1 and self._entid and self._entid != "":
                        _class_base = import_class(
                            "MambuPy.rest", self.mambuclassname)
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
                "_class", "_entid", "attrs",
                "__args", "__kwargs",
                "_MambuStruct__args", "_MambuStruct__kwargs",
                "wrapped1", "wrapped2",
                "mambuclassname", "mambuclass1", "mambuclass2",
                "mambubranchclass", "mambucentreclass", "mambuuserclass",
                "mambuclientclass", "mambugroupclass",
                "mamburepaymentclass",
                "mamburepaymentsclass", "mambutransactionclass",
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

    def connect(self, *args, **kwargs):
        self.__args = deepcopy(args)
        self.__kwargs.update(kwargs)

        if "entid" in self.__kwargs:
            self._entid = self.__kwargs["entid"]
            self.wrapped2 = self.mambuclass2.get(
                detailsLevel=self.detailsLevel, *self.__args, **self.__kwargs)
            self.attrs = self.wrapped2._attrs
            self.wrapped1 = None
            self.preprocess()
            self.postprocess()
        else:
            self._entid = ""
            entities = self.mambuclass2.get_all(
                detailsLevel=self.detailsLevel, *self.__args, **self.__kwargs)
            self.wrapped2 = []
            self.wrapped1 = None
            _class2 = import_class("MambuPy.rest1to2", self.mambuclassname)
            for entity in entities:
                obj = _class2(urlfunc=None, fullDetails=self.fullDetails)
                obj._entid = entity.id
                obj.wrapped2 = entity
                obj.attrs = obj.wrapped2._attrs
                obj.mambuclassname = self.mambuclassname
                obj.mambuclass1 = self.mambuclass1
                obj.preprocess()
                obj.postprocess()
                self.wrapped2.append(obj)

    def preprocess(self, *args, **kwargs):
        """"""

    def postprocess(self, *args, **kwargs):
        """"""

    def create(self, data, *args, **kwargs):
        self.wrapped2._attrs = data
        self.wrapped2.create()

        return 1

    def update(self, data, *args, **kwargs):
        fields = []
        for ci in data.get("customInformation", {}):
            self[ci["customFieldID"]] = ci["value"]
            fields.append(ci["customFieldID"])
        if fields:
            self.wrapped2.patch(fields=fields)

        self.wrapped2.update()

        return 1

    def update_post(self, data, *args, **kwargs):
        return self.update(data, *args, **kwargs)

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

    def setBranch(self, *args, **kwargs):
        try:
            self.mambubranchclass
        except AttributeError:
            from mambupy.rest1to2 import mambubranch
            self.mambubranchclass = mambubranch.MambuBranch

        self.branch = self.mambubranchclass(
            entid=self.wrapped2.assignedBranchKey, *args, **kwargs)
        self.assignedBranchName = self.branch.name
        self.assignedBranch = self.branch

        return 1

    def setCentre(self, *args, **kwargs):
        try:
            self.mambucentreclass
        except AttributeError:
            from mambupy.rest1to2 import mambucentre
            self.mambubranchclass = mambucentre.MambuCentre

        self.centre = self.mambucentreclass(
            entid=self.wrapped2.assignedCentreKey, *args, **kwargs)
        self.assignedCentreName = self.centre.name
        self.assignedCentre = self.centre

        return 1
