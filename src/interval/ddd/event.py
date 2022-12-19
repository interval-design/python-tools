"""
interval.ddd.event
~~~~~~~~~~~~~~~~~~

This module provides DDD event base classes.
"""

import dataclasses
import datetime

from .serialization import DataClassJsonMixin
from .valueobject import UUIDRef


@dataclasses.dataclass(frozen=True)
class DomainEventRef(UUIDRef):
    """领域事件唯一标识"""
    pass


@dataclasses.dataclass
class DomainEvent(DataClassJsonMixin):
    """领域事件"""
    ref: DomainEventRef = dataclasses.field(default_factory=DomainEventRef, init=False)

    @property
    def occurred_at(self) -> datetime.datetime:
        """事件发生时间（包含系统本地时区）"""
        return self.ref.created_at
