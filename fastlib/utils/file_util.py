# SPDX-License-Identifier: MIT

"""Path utility functions for locating project directories and files."""

from functools import lru_cache
from pathlib import Path
from typing import Optional, Union


class PathFinder:
    """Utility class for locating project directories and files."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize PathFinder with optional base path.

        Args:
            base_path: Starting path for searches. Defaults to current file's directory.
        """
        self.base_path = (
            Path(base_path) if base_path else Path(__file__).resolve().parent
        )

    @lru_cache(maxsize=32)
    def find_upward(
        self, target: str, start_path: Optional[Path] = None, max_depth: int = 20
    ) -> Path:
        """Find a file or directory by searching upward through parent directories.

        Args:
            target: Name of file or directory to find
            start_path: Starting directory for search (defaults to base_path)
            max_depth: Maximum levels to search upward (prevents infinite loops)

        Returns:
            Path to the found target

        Raises:
            FileNotFoundError: If target not found within max_depth levels
        """
        current = Path(start_path) if start_path else self.base_path

        for _ in range(max_depth):
            candidate = current / target
            if candidate.exists():
                return candidate.resolve()

            if current.parent == current:  # Reached filesystem root
                break
            current = current.parent

        raise FileNotFoundError(
            f"'{target}' not found within {max_depth} levels from {start_path or self.base_path}"
        )

    def find_project_root(self, markers: Union[str, list[str]] = None) -> Path:
        """Locate project root directory using marker files.

        Args:
            markers: Single marker or list of markers.
                    Defaults to common project markers.

        Returns:
            Path to project root directory

        Raises:
            FileNotFoundError: If no marker found
        """
        if markers is None:
            markers = ["pyproject.toml", "setup.py", ".git", "requirements.txt"]
        elif isinstance(markers, str):
            markers = [markers]

        for marker in markers:
            try:
                marker_path = self.find_upward(marker)
                return marker_path.parent if marker_path.is_file() else marker_path
            except FileNotFoundError:
                continue

        raise FileNotFoundError(
            f"No project root marker found. Tried: {', '.join(markers)}"
        )

    @property
    @lru_cache(maxsize=1)
    def project_root(self) -> Path:
        """Get cached project root directory."""
        return self.find_project_root()

    def get_resource_path(self, *parts: str) -> Path:
        """Get path relative to project root.

        Args:
            *parts: Path components relative to project root

        Returns:
            Resolved path
        """
        return self.project_root / Path(*parts)


# Create a default instance for convenience
_default_finder = PathFinder()


# Convenience functions that maintain backward compatibility
@lru_cache(maxsize=1)
def get_utils_dir() -> str:
    """Get the absolute path of the directory containing this utils module."""
    return str(Path(__file__).resolve().parent)


@lru_cache(maxsize=1)
def get_resource_dir() -> str:
    """Get the absolute path of the project's resource directory."""
    try:
        # Try to find project root and construct resource path
        project_root = _default_finder.find_project_root()
        resource_dir = project_root / "resource"

        # If resource dir doesn't exist at project root, fall back to relative path
        if not resource_dir.exists():
            # Fallback to the original logic (3 levels up)
            return str(
                Path(__file__).resolve().parent.parent.parent.parent / "resource"
            )

        return str(resource_dir)
    except FileNotFoundError:
        # Fallback to the original logic
        return str(Path(__file__).resolve().parent.parent.parent.parent / "resource")


def get_file_dir(marker_file: str) -> str:
    """Locate directory containing the specified marker file."""
    marker_path = _default_finder.find_upward(marker_file)
    return str(marker_path.parent if marker_path.is_file() else marker_path)


def get_file_path(marker_file: str) -> str:
    """Locate the absolute path of the specified marker file."""
    return str(_default_finder.find_upward(marker_file))


def find_project_root(marker_file: str = "pyproject.toml") -> Path:
    """Locate the project root directory by searching for a marker file."""
    return _default_finder.find_project_root(marker_file)


# Additional utility functions for common use cases
def get_project_path(*parts: str) -> Path:
    """Get a path relative to the project root.

    Args:
        *parts: Path components relative to project root

    Returns:
        Resolved Path object

    Example:
        >>> get_project_path("data", "input", "file.csv")
        Path('/home/user/project/data/input/file.csv')
    """
    return _default_finder.get_resource_path(*parts)


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
