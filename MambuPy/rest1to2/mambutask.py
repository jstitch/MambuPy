from mambupy.rest.mambutask import MambuTask as MambuTask1, MambuTasks as MambuTasks1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mamburestutils import MambuStructIterator


task_filters = ["username", "clientId", "groupId", "status"]


class MambuTask(MambuStruct, MambuTask1):
    entid_fld = "taskId"

    def __init__(self, *args, **kwargs):
        process_filters(task_filters, kwargs)
        super().__init__(*args, **kwargs)

    def __repr__(self):
        try:
            return self.__class__.__name__ + " - taskid: '%s', %s, %s" % (
                self.id,
                self.dueDate,
                self.status,
            )
        except AttributeError:
            try:
                return self.__class__.__name__ + " - taskid: '%s'" % self.id
            except AttributeError:
                try:
                    return self.__class__.__name__ + " - taskid: '%s', %s, %s" % (
                        self.id,
                        self.dueDate,
                        self.status,
                    )
                except AttributeError:
                    return self.__class__.__name__ + " - taskid: '%s'" % self.id

    def close(self, *args, **kwargs):
        from datetime import datetime

        self.status = "COMPLETED"
        self.wrapped2.patch(fields=["status"])


class MambuTasks(MambuStruct, MambuTasks1):
    entid_fld = "taskId"

    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuTask"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuTask
        process_filters(task_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
