"""
interval.ddd.dto
~~~~~~~~~~~~~~~~

This module provides DDD data transfer object base classes.
"""

import dataclasses

from .serialization import DataClassJsonMixin


@dataclasses.dataclass
class UseCaseDTO(DataClassJsonMixin):
    """用例返回的数据传输对象"""
    pass
