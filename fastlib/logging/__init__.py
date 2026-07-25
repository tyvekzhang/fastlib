# SPDX-License-Identifier: MIT
"""Export logging module"""

from .handlers import Logger

logger = Logger.initialize()

__all__ = [
    "logger",
]
