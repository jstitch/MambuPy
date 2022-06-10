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
    module = importlib.import_module(
        path + "." + _object.__class__.__name__.lower())
    _class = getattr(module, _object.__class__.__name__)

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

        process_filters(["limit", "offset"], kwargs)

        _class = import_class("MambuPy.api", self)

        if "urlfunc" in kwargs and kwargs["urlfunc"] is None:
            self.wrapped2 = _class()
            return

        if "entid" in kwargs:
            self.wrapped2 = _class.get(
                detailsLevel=self.detailsLevel, *args, **kwargs)
        else:
            entities = _class.get_all(
                detailsLevel=self.detailsLevel, *args, **kwargs)
            self.wrapped2 = []
            _class2 = import_class("MambuPy.rest1to2", self)
            for entity in entities:
                obj = _class2(urlfunc=None)
                obj.wrapped2 = entity
                self.wrapped2.append(obj)

    def __getitem__(self, key):
        try:
            item = super().__getitem__(key)
            return item
        except KeyError:
            try:
                item = self.wrapped2[key]
                return item
            except KeyError:
                if not self.wrapped1:
                    _class = import_class("MambuPy.rest", self)
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self.id)
                item = self.wrapped1[key]
                return item

    def __setitem__(self, key, value):
        self.wrapped2[key] = value

    def __getattribute__(self, name):
        try:
            attribute = super().__getattribute__(name)
            return attribute
        except AttributeError:
            try:
                attribute = getattr(self.wrapped2, name)
                return attribute
            except AttributeError:
                if not self.wrapped1:
                    _class = import_class("MambuPy.rest", self)
                    self.wrapped1 = _class(
                        fullDetails=self.fullDetails, entid=self.id)
                attribute = getattr(self.wrapped1, name)
                return attribute

    def __setattr__(self, name, value):
        if name not in ["attrs", "wrapped1", "wrapped2"]:
            self.wrapped2.__setattr__(name, value)
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return self.wrapped2.__str__()

    def __repr__(self):
        return self.wrapped2.__repr__()

    def __len__(self):
        return self.wrapped2.__len__()
