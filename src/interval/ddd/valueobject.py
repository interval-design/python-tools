"""
interval.ddd.valueobject
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides DDD ValueObject base class and derived classes.
"""

import dataclasses
import datetime
import typing
import uuid

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None


@dataclasses.dataclass(frozen=True)
class ValueObject:
    """值对象"""

    @classmethod
    def composite_factory(cls, *args) -> typing.Self | None:
        """一个工厂方法，用于支持SQLAlchemy ORM的“复合列类型”，对于“嵌套复合”不适用"""
        for arg in args:
            if arg is not None:
                return cls(*args)  # noqa


@dataclasses.dataclass(frozen=True)
class IntegerRef(ValueObject):
    """唯一标识（整数）"""
    value: int


@dataclasses.dataclass(frozen=True)
class StringRef(ValueObject):
    """唯一标识（字符串）"""
    value: str


def _gen_uuid_str() -> str:
    return uuid.uuid1().hex


@dataclasses.dataclass(frozen=True)
class UUIDRef(StringRef):
    """唯一标识（UUID）"""
    value: str = dataclasses.field(default_factory=_gen_uuid_str)

    @property
    def typed_value(self) -> uuid.UUID:
        return uuid.UUID(self.value)

    @property
    def created_at(self) -> datetime.datetime:
        """标识创建时间（包含系统本地时区）"""
        t = (self.typed_value.time - 0x01b21dd213814000) / 10_000_000
        return datetime.datetime.fromtimestamp(t).astimezone()


def _gen_oid_str() -> str:
    if ObjectId is None:
        raise RuntimeError('PyMongo package is not installed')
    return str(ObjectId())


@dataclasses.dataclass(frozen=True)
class OIDRef(StringRef):
    """唯一标识（ObjectId）"""
    value: str = dataclasses.field(default_factory=_gen_oid_str)

    @property
    def typed_value(self) -> ObjectId:
        if ObjectId is None:
            raise RuntimeError('PyMongo package is not installed')
        return ObjectId(self.value)

    @property
    def created_at(self) -> datetime.datetime:
        """标识创建时间（包含系统本地时区）"""
        return self.typed_value.generation_time.astimezone()
