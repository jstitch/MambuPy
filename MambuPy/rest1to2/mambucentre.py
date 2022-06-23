from mambupy.rest.mambucentre import MambuCentre as MambuCentre1
from mambupy.rest1to2.mambustruct import MambuStruct


class MambuCentre(MambuStruct, MambuCentre1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
