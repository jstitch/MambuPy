from mambupy.rest.mambugroup import MambuGroup as MambuGroup1, MambuGroups as MambuGroups1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mambustruct import MambuStructIterator


class MambuGroup(MambuStruct, MambuGroup1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setBranch(self, *args, **kwargs):
        from mambupy.rest1to2 import mambubranch
        self.branch = mambubranch.MambuBranch(
            entid=self.wrapped2.assignedBranchKey, *args, **kwargs)

    def setCentre(self, *args, **kwargs):
        from mambupy.rest1to2 import mambucentre
        self.centre = mambucentre.MambuCentre(
            entid=self.wrapped2.assignedCentreKey, *args, **kwargs)

    def updatePatch(self, data, *args, **kwargs):
        if data.get("group"):
            for k, v in data["group"].items():
                data[k] = v
            del data["group"]
        super().updatePatch(data, *args, **kwargs)


class MambuGroups(MambuStruct, MambuGroups1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuGroup"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuGroup
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
