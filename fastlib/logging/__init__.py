# SPDX-License-Identifier: MIT
"""Export logging module"""

from .handlers import Logger

__all__ = [
    "Logger",
    "logger",
]


def __getattr__(name: str) -> Logger:
    if name == "logger":
        return Logger.initialize()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
