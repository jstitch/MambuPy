import importlib

from mambupy.rest.mambustruct import MambuStruct as MambuStruct1


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

        module = importlib.import_module(
            "mambupy.api." + self.__class__.__name__.lower())
        _class = getattr(module, self.__class__.__name__)
        self.wrapped2 = _class.get(
            detailsLevel=self.detailsLevel, *args, **kwargs)

    def __getitem__(self, key):
        return self.wrapped2[key]

    def __setitem__(self, key, value):
        self.wrapped2[key] = value

    def __getattribute__(self, name):
        try:
            attribute = super().__getattribute__(name)
            return attribute
        except AttributeError:
            attribute = getattr(self.wrapped2, name)
            return attribute

    def __setattr__(self, name, value):
        if name not in ["attrs", "wrapped1", "wrapped2"]:
            self.wrapped2.__setattr__(name, value)
        else:
            object.__setattr__(self, name, value)
