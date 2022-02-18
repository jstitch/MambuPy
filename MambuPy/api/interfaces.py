"""Interfaces for Mambu Objects."""

class MambuAttachable():
    """An entity which can attach documents"""

    _ownerType = ""
    """attachments owner type of this entity"""

    _attachments = {}
    """dict of attachments of an entity, key is the id"""
