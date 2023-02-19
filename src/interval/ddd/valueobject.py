"""
interval.ddd.valueobject
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides DDD ValueObject base class and derived classes.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None


@dataclass(frozen=True)
class ValueObject:
    """值对象"""

    @classmethod
    def composite_factory(cls, *args) -> Self | None:
        """一个工厂方法，用于支持SQLAlchemy ORM的“复合列类型”，对于“嵌套复合”不适用"""
        for arg in args:
            if arg is not None:
                return cls(*args)  # noqa


@dataclass(frozen=True)
class IntegerRef(ValueObject):
    """唯一标识（整数）"""
    value: int


@dataclass(frozen=True)
class StringRef(ValueObject):
    """唯一标识（字符串）"""
    value: str


def _gen_uuid_str() -> str:
    return uuid.uuid1().hex


@dataclass(frozen=True)
class UUIDRef(StringRef):
    """唯一标识（UUID）"""
    value: str = field(default_factory=_gen_uuid_str)

    @property
    def typed_value(self) -> uuid.UUID:
        return uuid.UUID(self.value)

    @property
    def created_at(self) -> datetime:
        """标识创建时间（包含系统本地时区）"""
        t = (self.typed_value.time - 0x01b21dd213814000) / 10_000_000
        return datetime.fromtimestamp(t).astimezone()


def _gen_oid_str() -> str:
    if ObjectId is None:
        raise RuntimeError('PyMongo package is not installed')
    return str(ObjectId())


@dataclass(frozen=True)
class OIDRef(StringRef):
    """唯一标识（ObjectId）"""
    value: str = field(default_factory=_gen_oid_str)

    @property
    def typed_value(self) -> ObjectId:
        if ObjectId is None:
            raise RuntimeError('PyMongo package is not installed')
        return ObjectId(self.value)

    @property
    def created_at(self) -> datetime:
        """标识创建时间（包含系统本地时区）"""
        return self.typed_value.generation_time.astimezone()
