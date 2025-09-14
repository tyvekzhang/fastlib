# SPDX-License-Identifier: MIT
"""Base configuration classes."""

from abc import ABC, abstractmethod


class BaseConfig(ABC):
    """Base class for all configuration classes."""

    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of the configuration.

        Returns:
            str: String representation of the configuration instance.
        """
        pass
