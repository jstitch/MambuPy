"""MambuTask entity: a MambuEntity struct for Tasks.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""
from .entities import (MambuEntity, MambuEntityWritable)


class MambuTask(MambuEntity, MambuEntityWritable):
    """MambuTask entity"""

    _prefix = "tasks"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
        "username",
        "clientId",
        "groupId",
        "status",
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
    ]
    """allowed fields for get_all sorting"""

    _taskLinkTypes = [
        "CLIENT",
        "GROUP",
        "BRANCH",
        "USER",
        "LOAN_ACCOUNT",
        "DEPOSIT_ACCOUNT",
        "ID_DOCUMENT",
        "LINE_OF_CREDIT",
        "GL_JOURNAL_ENTRY"]

    _entities = [
        ("assignedUserKey", "mambuuser.MambuUser", "assignedUser")]
    """3-tuples of elements and Mambu Entities"""
    @classmethod
    def get(cls, taskId):
        """get, a single task, identified by its taskId.

        Args:
          taskId (str): ID for the task

        Returns:
          instance of a task with data from Mambu
        """
        return super().get(entid=taskId)
