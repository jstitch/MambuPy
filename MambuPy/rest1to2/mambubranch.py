from mambupy.rest.mambubranch import MambuBranch as MambuBranch1
from mambupy.rest.mambubranch import MambuBranches as MambuBranches1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mamburestutils import MambuStructIterator


class MambuBranch(MambuStruct, MambuBranch1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def preprocess(self):
        from mambupy.rest1to2 import mambuuser
        self.mambuusersclass = mambuuser.MambuUsers

        try:
            self.address = self.addresses[0]
            for name, item in self.addresses[0].items():
                try:
                    self.addresses[0][name] = item.strip()
                    self.address[name] = item.strip()
                except AttributeError:
                    pass
        except (IndexError, AttributeError):
            pass

    def postprocess(self):
        try:
            for name, item in self.addresses[0].items():
                try:
                    if name == "indexInList":
                        continue
                    self.addresses[0][name] = str(self.addresses[0][name])
                    self.address[name] = str(self.address[name])
                except AttributeError:
                    pass
        except (IndexError, AttributeError):
            pass

    def setUsers(self, *args, **kwargs):
        try:
            self.mambuusersclass
        except AttributeError:
            from .mambuuser import MambuUsers
            self.mambuusersclass = MambuUsers

        usrs = [
            us
            for us in self.mambuusersclass(branchId=self["id"], *args, **kwargs)
            if us["userState"] == "ACTIVE"
        ]
        self["users"] = usrs

        return 1


class MambuBranches(MambuStruct, MambuBranches1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuBranch"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuBranch
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
