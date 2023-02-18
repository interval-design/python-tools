"""
interval.ddd.event
~~~~~~~~~~~~~~~~~~

This module provides DDD event base classes.
"""

import dataclasses
import datetime
import uuid


@dataclasses.dataclass
class DomainEvent:
    """领域事件

    Attributes:
        id: 事件ID
        occurred_at: 事件发生时间（包含系统本地时区）
    """
    id: str = dataclasses.field(
        default_factory=lambda: str(uuid.uuid1()),
        init=False
    )
    occurred_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now().astimezone(),
        init=False
    )
