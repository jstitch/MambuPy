from mambupy.rest.mambuclient import MambuClient as MambuClient1, MambuClients as MambuClients1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mambustruct import MambuStructIterator

from ..mambuutil import strip_consecutive_repeated_char as scrc


class MambuClient(MambuStruct, MambuClient1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def preprocess(self):
        from mambupy.rest1to2 import mambubranch, mambugroup

        self.mambubranchclass = mambubranch.MambuBranch
        self.mambugroupclass = mambugroup.MambuGroup

        try:
            self.firstName = scrc(self.wrapped2.firstName, " ").strip()
        except Exception:
            self.firstName = ""
        try:
            self.middleName = scrc(self.wrapped2.middleName, " ").strip()
        except Exception:
            self.middleName = ""
        self.givenName = scrc(
            self.firstName +
            ((" " + self.middleName) if self.middleName != "" else ""),
            " ",
        ).strip()
        self.lastName = scrc(self.wrapped2.lastName, " ").strip()
        self.firstLastName = (
            " ".join(self.lastName.split(" ")[:-1])
            if len(self.lastName.split(" ")) > 1
            else self.lastName
        )
        self.secondLastName = (
            " ".join(self.lastName.split(" ")[-1:])
            if len(self.lastName.split(" ")) > 1
            else ""
        )

        self.name = scrc("%s %s" % (self.givenName, self.lastName), " ").strip()

        try:
            self.address = self.addresses[0]
            for name, item in self.addresses[0].items():
                try:
                    self.addresses[0][name] = item.strip()
                    self.address[name] = item.strip()
                except AttributeError:
                    pass
        except (KeyError, IndexError):
            pass

        try:
            for idDoc in self.idDocuments:
                self[idDoc.documentType] = idDoc.documentId
        except KeyError:
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
        except (KeyError, IndexError):
            pass

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

    def setGroups(self, *args, **kwargs):
        requests = 0
        groups = []
        try:
            self.mambugroupclass
        except AttributeError:
            from mambupy.rest1to2 import mambugroup
            self.mambugroupclass = mambugroup.MambuGroup
        try:
            for gk in self.groupKeys:
                g = self.mambugroupclass(entid=gk, *args, **kwargs)
                requests += 1
                groups.append(g)
        except AttributeError:
            pass
        self.groups = groups
        return requests

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
