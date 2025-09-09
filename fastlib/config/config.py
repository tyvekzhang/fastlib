# SPDX-License-Identifier: MIT
"""Base configuration classes."""

from abc import ABC, abstractmethod


class BaseConfig(ABC):
    """Abstract base class for all configuration classes."""

    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize configuration with keyword arguments."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of the configuration."""
        pass


