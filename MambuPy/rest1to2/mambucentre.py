from mambupy.rest.mambucentre import MambuCentre as MambuCentre1
from mambupy.rest.mambucentre import MambuCentres as MambuCentres1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mamburestutils import MambuStructIterator


centre_filters = ["branchId"]


class MambuCentre(MambuStruct, MambuCentre1):
    def __init__(self, *args, **kwargs):
        process_filters(centre_filters, kwargs)
        super().__init__(*args, **kwargs)


class MambuCentres(MambuStruct, MambuCentres1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuCentre"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuCentre
        process_filters(centre_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
