"""
interval.utils
~~~~~~~~~~~~~~

This module provides utility functions.
"""

import random
import re
import string
from decimal import Decimal
from logging import Filter, Formatter, getLogger, Logger, LogRecord, StreamHandler
from typing import Any, Callable

import orjson


def safe_issubclass(class_or_object, classinfo):
    try:
        return issubclass(class_or_object, classinfo)
    except TypeError:
        return False


def _orjson_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if callable(getattr(obj, 'to_dict', None)):
        return obj.to_dict()
    try:
        return list(obj)
    except Exception:
        raise TypeError


def orjson_dumps(obj: Any) -> bytes:
    """使用orjson进行JSON序列化操作

    除了orjson默认支持的数据类型，还支持以下对象：
    1、Decimal对象，转化为字符串；
    2、带有to_dict()方法的对象，转化为字典；
    3、可迭代对象，转化为列表。

    Args:
        obj: Python对象

    Returns:
        JSON字节流

    Raises:
        orjson.JSONEncodeError: TypeError的子类
    """
    return orjson.dumps(
        obj,
        default=_orjson_default,
        option=orjson.OPT_OMIT_MICROSECONDS | orjson.OPT_SERIALIZE_NUMPY
    )


def orjson_loads(obj: bytes | bytearray | memoryview | str) -> Any:
    """使用orjson进行JSON反序列化操作

    Args:
        obj: JSON字节流或字符串

    Returns:
        Python对象

    Raises:
        orjson.JSONDecodeError: ValueError的子类
    """
    return orjson.loads(obj)


def get_stream_logger(name: str, level: int | str,
                      filters: list[Filter | Callable[[LogRecord], Any]] = None,
                      formatter: Formatter = None) -> Logger:
    """获取日志记录器（日志输出到sys.stderr）

    Args:
        name: 日志名称
        level: 日志级别
        filters: logging.Filter实例（或者以logging.LogRecord实例作为参数的函数）列表
        formatter: logging.Formatter实例

    Returns:
        日志记录器
    """
    logger = getLogger(name)
    logger.setLevel(level)
    if filters:
        for f in filters:
            logger.addFilter(f)
    handler = StreamHandler()
    handler.setLevel(level)
    if formatter is not None:
        handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def generate_nonce(length: int, chars: str = 'uld', population: str = '',
                   *, prefix: str = '', suffix: str = '') -> str:
    """生成固定长度的随机字符串

    Args:
        length: 字符串总长度
        chars: 使用的字符种类，可组合使用：'u' - 大写字母，'l' - 小写字母，'d' - 数字
        population: 使用的字符集合；若指定了population则忽略chars
        prefix: 字符串前缀
        suffix: 字符串后缀

    Returns:
        随机字符串

    Raises:
        ValueError: 前缀和后缀的长度之和大于总长度；没有指定有效的字符种类或者字符集合
    """
    random_part_len = length - len(prefix + suffix)
    if random_part_len < 0:
        raise ValueError('Invalid length')
    if random_part_len == 0:
        return prefix + suffix
    if not population:
        if 'u' in chars:
            population += string.ascii_uppercase
        if 'l' in chars:
            population += string.ascii_lowercase
        if 'd' in chars:
            population += string.digits
        if not population:
            raise ValueError('Invalid chars')
    elements = random.choices(population, k=random_part_len)
    return prefix + ''.join(elements) + suffix


def check_mobile_number(number: str) -> bool:
    """检查手机号码格式是否正确

    Args:
        number: 手机号码

    Returns:
        格式正确返回True，否则返回False
    """
    pattern = r'1[3-9]\d{9}'
    match_obj = re.fullmatch(pattern, number)
    return bool(match_obj)


def check_id_card_number(number: str) -> bool:
    """检查身份证号码格式是否正确

    Args:
        number: 身份证号码

    Returns:
        格式正确返回True，否则返回False
    """
    if len(number) == 18:
        pattern = r'[1-9]\d{5}[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dxX]'
        match_obj = re.fullmatch(pattern, number)
        return bool(match_obj)
    if len(number) == 15:
        pattern = r'[1-9]\d{7}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}'
        match_obj = re.fullmatch(pattern, number)
        return bool(match_obj)
    return False
