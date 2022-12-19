"""
interval.ddd.serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides DDD serialization mixins.
"""

import dataclasses
import datetime
import decimal
import enum
import json
import typing
import uuid

from .valueobject import IntegerRef, StringRef


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
