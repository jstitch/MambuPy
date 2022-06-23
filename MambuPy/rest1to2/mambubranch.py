from mambupy.rest.mambubranch import MambuBranch as MambuBranch1
from mambupy.rest1to2.mambustruct import MambuStruct


class MambuBranch(MambuStruct, MambuBranch1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
