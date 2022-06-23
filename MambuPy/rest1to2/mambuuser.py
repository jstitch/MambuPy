from mambupy.rest.mambuuser import MambuUser as MambuUser1
from mambupy.rest1to2.mambustruct import MambuStruct


class MambuUser(MambuStruct, MambuUser1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
