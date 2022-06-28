from mambupy.rest.mambuclient import MambuClient as MambuClient1, MambuClients as MambuClients1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mambustruct import MambuStructIterator


class MambuClient(MambuStruct, MambuClient1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setBranch(self, *args, **kwargs):
        from mambupy.rest1to2 import mambubranch
        self.branch = mambubranch.MambuBranch(
            entid=self.wrapped2.assignedBranchKey, *args, **kwargs)

    def updatePatch(self, data, *args, **kwargs):
        if data.get("client"):
            for k, v in data["client"].items():
                data[k] = v
            del data["client"]
        super().updatePatch(data, *args, **kwargs)


class MambuClients(MambuStruct, MambuClients1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuClient"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuClient
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
