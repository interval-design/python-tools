"""
interval.ddd
~~~~~~~~~~~~

This package provides basic components of Domain-Driven Design.
"""

from .dto import UseCaseDTO
from .entity import Entity, Aggregate
from .event import DomainEvent
from .exceptions import (
    DDDException,
    DomainException,
    ServiceLayerException,
    AdapterException,
    RemoteServiceException,
    DBAPIError,
    InterfaceError,
    DatabaseError,
    DataError,
    OperationalError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError,
    DBAPIErrorWrapper,
    STANDARD_DBAPI_ERRORS
)
from .messagebus import AbstractMessageBus
from .repo import Repository
from .uow import AbstractUnitOfWork
from .valueobject import (
    ValueObject,
    IntegerRef,
    StringRef,
    UUIDRef,
    OIDRef
)
