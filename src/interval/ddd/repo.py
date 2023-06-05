"""
interval.ddd.repo
~~~~~~~~~~~~~~~~~

This module provides DDD repository base classes.
"""

from .entity import Aggregate


class Repository:
    """资源库

    Attributes:
        seen: 跟踪在读写操作期间加载的聚合
    """

    def __init__(self):
        self.seen: set[Aggregate] = set()
