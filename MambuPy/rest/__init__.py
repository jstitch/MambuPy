# coding: utf-8
"""MambuPy REST module - DEPRECATED.

.. warning::

   DEPRECATED: This module uses Mambu API v1 which is no longer supported.
   This code is maintained only for backwards compatibility with legacy systems.
   It will be removed in a future version of MambuPy.

   Only mambuactivity is available in this legacy module.
"""
import warnings

warnings.warn(
    "MambuPy.rest module is deprecated and will be removed in a future version. "
    "Mambu API v1 is no longer supported by Mambu.",
    DeprecationWarning,
    stacklevel=2,
)

from .mambuactivity import (
    MambuActivity,
    MambuActivities,
    getactivitiesurl,
)

__all__ = [
    "MambuActivity",
    "MambuActivities",
    "getactivitiesurl",
]
