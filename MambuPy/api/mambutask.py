"""MambuTask entity: a MambuEntity struct for Tasks.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy

from .entities import MambuEntity, MambuEntityWritable


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

    _sortBy_fields = []
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
        "GL_JOURNAL_ENTRY",
    ]

    _entities = [
        ("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
        ("taskLinkKey", "", "taskLink"),
    ]
    """3-tuples of elements and Mambu Entities"""

    def __init__(self, **kwargs):
        self._entities = copy.deepcopy(MambuTask._entities)
        super().__init__(**kwargs)

    def _assignEntObjs(
        self, entities=None, detailsLevel="BASIC", get_entities=False, debug=False
    ):
        """Overwrites `MambuPy.api.mambustruct._assignEntObjs` for MambuTask

        Determines the type of task link and instantiates accordingly
        """
        if entities is None:
            entities = self._entities

        try:
            tasklink_index = entities.index(("taskLinkKey", "", "taskLink"))
        except ValueError:
            tasklink_index = None

        if tasklink_index is not None and self.has_key("taskLinkKey"):
            if self.taskLinkType == "CLIENT":
                entities[tasklink_index] = (
                    "taskLinkKey",
                    "mambuclient.MambuClient",
                    "taskLink",
                )
            elif self.taskLinkType == "GROUP":
                entities[tasklink_index] = (
                    "taskLinkKey",
                    "mambugroup.MambuGroup",
                    "taskLink",
                )

        return super()._assignEntObjs(
            entities, detailsLevel=detailsLevel, get_entities=get_entities, debug=debug
        )

    @classmethod
    def get(cls, taskId, **kwargs):
        """get, a single task, identified by its taskId.

        Args:
          taskId (str): ID for the task

        Returns:
          instance of a task with data from Mambu
        """
        return super().get(entid=taskId, **kwargs)
