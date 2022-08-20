from mambupy.rest.mambugroup import MambuGroup as MambuGroup1, MambuGroups as MambuGroups1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mamburestutils import MambuStructIterator


group_filters = ["branchId", "centreId", "creditOfficerUsername"]


class MambuGroup(MambuStruct, MambuGroup1):
    def __init__(self, *args, **kwargs):
        process_filters(group_filters, kwargs)
        super().__init__(*args, **kwargs)

    def preprocess(self):
        from mambupy.rest1to2 import mambubranch, mambucentre
        from mambupy.rest1to2 import mambuclient

        self.mambubranchclass = mambubranch.MambuBranch
        self.mambucentreclass = mambucentre.MambuCentre
        self.mambuclientclass = mambuclient.MambuClient

        try:
            self.notes = self.notes.replace("<div>", "").replace("</div>", "")
        except Exception:
            self.notes = ""

        try:
            self.name = self.groupName
        except AttributeError:
            pass

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

    def setClients(self, *args, **kwargs):
        requests = super().setClients(*args, **kwargs)
        for member in self.groupMembers:
            member.client = [
                cl for cl in self.clients
                if cl.encodedKey == member.clientKey][0]
        return requests

    def setActivities(self, *args, **kwargs):
        try:
            self.mambuactivitiesclass
        except AttributeError:
            from mambupy.rest1to2 import mambuactivity
            self.mambuactivitiesclass = mambuactivity.MambuActivities

        def activity_date(activity):
            try:
                return activity["activity"]["timestamp"]
            except KeyError:
                return None
        activities = self.mambuactivitiesclass(loanAccountId=self.encodedKey, *args, **kwargs)
        activities.attrs = sorted(activities.attrs, key=activity_date)
        self["activities"] = activities

        return 1

    def addMembers(self, newMembers=[], *args, **kwargs):
        from mambupy.api.vos import MambuGroupMember
        newGroupMembers = [
            MambuGroupMember(**{"clientKey": cek})
            for cek in newMembers
            if cek not in [gm.clientKey for gm in self.groupMembers]
        ]
        self.groupMembers.extend(newGroupMembers)
        self.patch(["groupMembers"])

        return 1

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
        process_filters(group_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
