from mambupy.rest.mambuproduct import MambuProduct as MambuProduct1
from mambupy.rest1to2.mambustruct import MambuStruct


class MambuProduct(MambuStruct, MambuProduct1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
