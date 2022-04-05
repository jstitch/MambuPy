"""MambuTask entity: a MambuEntity struct for Tasks.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .mambustruct import (MambuEntity, MambuEntityWritable)


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

    @classmethod
    def get(cls, taskId):
        """get, a single task, identified by its taskId.

        Args:
          taskId (str): ID for the task

        Returns:
          instance of a task with data from Mambu
        """
        return super().get(entid=taskId)
