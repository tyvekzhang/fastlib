"""Exception handling."""

from .base import HTTPException
from .exception_manager import register_exception_handlers

__all__ = [HTTPException, register_exception_handlers]
