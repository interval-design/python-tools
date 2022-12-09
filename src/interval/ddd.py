"""
interval.ddd
~~~~~~~~~~~~

This module provides basic components of Domain-Driven Design.
"""

import dataclasses
import datetime
import decimal
import enum
import functools
import json
import sys
import typing
import uuid

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None


__all__ = [
    'Entity',
    'Aggregate',
    'ValueObject',
    'IntegerRef',
    'StringRef',
    'UUIDRef',
    'OIDRef',
    'DataClassJsonMixin',
    'DomainEventRef',
    'DomainEvent',
    'UseCaseDTO',
    'DomainException',
    'ServiceLayerException',
    'AdapterException',
    'RemoteServiceException',
    'DBAPIError',
    'InterfaceError',
    'DatabaseError',
    'DataError',
    'OperationalError',
    'IntegrityError',
    'InternalError',
    'ProgrammingError',
    'NotSupportedError',
    'DBAPIErrorWrapper',
    'STANDARD_DBAPI_ERRORS'
]


# Entity; Aggregate Root Entity

class Entity:
    """实体

    Attributes:
        ref: 唯一标识
    """

    def __init__(self, ref):
        self.ref = ref

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.ref == self.ref

    def __hash__(self):
        return hash(self.ref)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.ref!r}>'


class Aggregate(Entity):
    """聚合根实体

    Attributes:
        ref: 唯一标识
        version_number: 版本号，用于支持乐观锁
        domain_events: 领域事件列表
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.domain_events = []
        return obj

    def __init__(self, ref, version_number: int = 1):
        super().__init__(ref)
        self.version_number = version_number


# Value Object; Unique Reference

@dataclasses.dataclass(frozen=True)
class ValueObject:
    """值对象"""

    @classmethod
    def composite_factory(cls, *args) -> typing.Self | None:
        """To support SQLAlchemy's ORM feature: Composite Column Types"""
        for arg in args:
            if arg is not None:
                return cls(*args)  # noqa

    def __composite_values__(self) -> tuple:
        """To support SQLAlchemy's ORM feature: Composite Column Types"""
        return dataclasses.astuple(self)


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


# Domain Event；Data Transfer Object

Json = typing.Union[dict, list, str, int, float, bool, None]


class DataClassJsonMixin:
    """将dataclass实例转换成JSON字符串

    递归支持以下属性类型：dataclass/dict/list/tuple/set/date/time/Decimal/Enum/UUID/str/int/float/bool/None；
    如果存在不支持的类型，则抛出TypeError异常。
    """

    def to_dict(self) -> dict[str, Json]:
        """转换成可以直接序列化为JSON字符串的字典

        Raises:
            TypeError
        """
        return _as_dict(self)

    def to_json(self, **kwargs) -> str:
        """转换成JSON字符串

        Args:
            kwargs: 关键字参数直接传递给json.dumps

        Raises:
            TypeError
        """
        kvs = self.to_dict()
        return json.dumps(kvs, **kwargs)


def _as_dict(obj) -> Json:
    if isinstance(obj, IntegerRef | StringRef):
        return obj.value
    elif _is_dataclass_instance(obj):
        return {field.name: _as_dict(getattr(obj, field.name)) for field in dataclasses.fields(obj)}
    elif isinstance(obj, dict):
        return {str(k): _as_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list | tuple | set):
        return [_as_dict(v) for v in obj]
    elif isinstance(obj, datetime.date | datetime.time):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, enum.Enum):
        return _as_dict(obj.value)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Json):
        return obj
    else:
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')


def _is_dataclass_instance(obj):
    return dataclasses.is_dataclass(obj) and not isinstance(obj, type)


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


@dataclasses.dataclass
class UseCaseDTO(DataClassJsonMixin):
    """用例返回的数据传输对象"""
    pass


# Exceptions; DBAPIError Wrapper

class DomainException(Exception):
    """领域异常"""
    pass


class ServiceLayerException(Exception):
    """服务层异常"""
    pass


class AdapterException(Exception):
    """适配器异常"""
    pass


class RemoteServiceException(AdapterException):
    """远程服务异常"""
    pass


class DBAPIError(AdapterException):
    """Wraps a DB-API 2.0 Error"""

    @property
    def orig(self) -> Exception | None:
        """Original exception"""
        return self.__cause__

    def __str__(self):
        if self.orig:
            return self.orig.__str__()
        else:
            return super().__str__()


class InterfaceError(DBAPIError): pass
class DatabaseError(DBAPIError): pass
class DataError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class InternalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass


class DBAPIErrorWrapper:
    """DBAPIError包装器

    将数据库适配器抛出的异常转换成相应的统一定义的DBAPIError；作为装饰器或上下文管理器使用。

    Attributes:
        errors: 异常名称与DBAPIError类型的对应关系；默认使用STANDARD_DBAPI_ERRORS
        default: 如果没有在errors中找到对应关系，则将异常转换成该属性指定的DBAPIError类型；默认为None，不进行默认转换
    """

    def __init__(self,
                 errors: dict[str, type[DBAPIError]] = None,
                 default: type[DBAPIError] = None):
        if errors is None:
            self.errors = STANDARD_DBAPI_ERRORS
        else:
            self.errors = errors
        self.default = default

    def raise_from(self, exc_type, exc_val, exc_tb):
        if exc_type.__name__ in self.errors:
            new_type = self.errors[exc_type.__name__]
        elif self.default:
            new_type = self.default
        else:
            return
        new_exc = new_type(*exc_val.args)
        if exc_tb:
            raise new_exc.with_traceback(exc_tb) from exc_val
        else:
            raise new_exc from exc_val

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        self.raise_from(exc_type, exc_val, exc_tb)

    def __call__(self, func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                self.raise_from(*sys.exc_info())
                raise
        return _wrapper


STANDARD_DBAPI_ERRORS = {
    'InterfaceError': InterfaceError,
    'DatabaseError': DatabaseError,
    'DataError': DataError,
    'OperationalError': OperationalError,
    'IntegrityError': IntegrityError,
    'InternalError': InternalError,
    'ProgrammingError': ProgrammingError,
    'NotSupportedError': NotSupportedError
}
