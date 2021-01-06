import enum
from typing import Optional

from pydantic.main import BaseModel


class BuildConfOutputModel(BaseModel):
    href: str
    id: str  # noqa: A003
    name: str
    projectId: str
    projectName: str


class BaseLocatorModel(BaseModel):
    id: Optional[str] = None  # noqa: A003
    name: Optional[str] = None

    def __str__(self):
        return ",".join(map(":".join, self.dict(exclude_none=True).items()))


class BuildConfLocator(BaseLocatorModel):
    project: Optional[str]
    template: Optional[str]


class BuildStateEnum(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"


class BuildStatusEnum(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"


class QueuedBuildDetailsModel(BaseModel):
    id: int  # noqa: A003
    state: BuildStateEnum
    status: Optional[BuildStatusEnum]
