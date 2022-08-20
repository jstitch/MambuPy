from mambupy.rest.mambuuser import MambuUser as MambuUser1, MambuUsers as MambuUsers1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mamburestutils import MambuStructIterator


user_filters = ["branchId"]


class MambuUser(MambuStruct, MambuUser1):
    def __init__(self, *args, **kwargs):
        process_filters(user_filters, kwargs)
        super().__init__(*args, **kwargs)

    def preprocess(self):
        from mambupy.rest1to2 import mambubranch, mambugroup

        self.mambubranchclass = mambubranch.MambuBranch
        self.mambugroupsclass = mambugroup.MambuGroups

        try:
            self.firstName = self.firstName.strip()
        except AttributeError:
            self.firstName = ""
        try:
            self.lastName = self.lastName.strip()
        except AttributeError:
            self.lastName = ""

        self.name = self.firstName + " " + self.lastName

    def setGroups(self, *args, **kwargs):
        if "fullDetails" in kwargs:
            fullDetails = kwargs["fullDetails"]
            kwargs.pop("fullDetails")
        else:
            fullDetails = True

        try:
            self.mambugroupsclass
        except AttributeError:
            from mambupy.rest1to2 import MambuGroups
            self.mambugroupsclass = MambuGroups

        groups = self.mambugroupsclass(
            creditOfficerUsername=self.username,
            fullDetails=fullDetails,
            *args, **kwargs
        )
        self.groups = groups

        return 1

    def setRoles(self, *args, **kwargs):
        # TODO implement setRoles with v2 MambuRole
        # which still doesn't exists on api module
        requests = 0
        try:
            role = self.role
        except AttributeError:
            return 0
        self.role.role = role

        return requests


class MambuUsers(MambuStruct, MambuUsers1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuUser"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuUser
        process_filters(user_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
