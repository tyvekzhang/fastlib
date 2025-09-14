# SPDX-License-Identifier: MIT
"""Configuration module util"""

import configparser
from pathlib import Path
from typing import Any, NamedTuple, Optional
from urllib.parse import urlparse

from loguru import logger

from fastlib.enums.enum import DBTypeEnum
from fastlib.utils import file_util

try:
    import tomllib
except ModuleNotFoundError:
    import toml as tomllib
except Exception:
    logger.error(
        "Cannot find tomllib module, please install it via `uv add tomllib` or `pip install tomllib`"
    )


class ProjectInfo:
    """
    A utility class for loading project metadata from pyproject.toml.

    Attributes:
        name (str): Project name.
        version (str): Project version.
        description (str): Project description.
        authors (list[str]): List of project authors.
    """

    def __init__(
        self,
        name: str,
        version: str,
        description: Optional[str] = None,
        authors: Optional[list[str]] = None,
    ):
        self.name = name
        self.version = version
        self.description = description or ""
        self.authors = authors or []

    @classmethod
    def from_pyproject(cls, pyproject_path: str = "") -> "ProjectInfo":
        """
        Load project information from a pyproject.toml file.

        Args:
            pyproject_path (str): The path to the pyproject.toml file.

        Returns:
            ProjectInfo: An instance containing project metadata.
        """
        if not pyproject_path:
            path = Path(file_util.find_project_root()) / "pyproject.toml"
        else:
            path = Path(pyproject_path)
        if not path.exists():
            raise FileNotFoundError(f"{pyproject_path} does not exist")

        # Use tomllib (Python 3.11+) or fall back to toml for older versions.
        with open(path, "rb" if tomllib.__name__ == "tomllib" else "r") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        authors = []
        if "authors" in project:
            authors = [
                a.get("name", "")
                for a in project.get("authors", [])
                if isinstance(a, dict)
            ]

        return cls(
            name=project.get("name", ""),
            version=project.get("version", ""),
            description=project.get("description", ""),
            authors=authors,
        )

    def as_dict(self) -> dict[str, str]:
        """
        Convert the project metadata into a dictionary.

        Returns:
            dict: Project information in key-value pairs.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
        }

    def __str__(self):
        """Return a readable string representation of the project."""
        return f"{self.name} v{self.version} — {self.description}"


class DbConnectionInfo(NamedTuple):
    """Container for parsed database connection information.

    Attributes:
        driver: Database driver (e.g., 'postgresql', 'mysql').
        username: Database username.
        password: Database password.
        host: Database host address.
        port: Database port number.
        dbname: Database name.
        full_url: Original full connection URL (with password masked for safety).
    """

    driver: str
    username: str
    password: str
    host: str
    port: str
    dbname: str
    full_url: str


def get_alembic_db_info(
    config_path: str,
) -> DbConnectionInfo:
    """Extracts and parses the SQLAlchemy URL from alembic.ini.

    Args:
        config_path: Path to the alembic.ini file.

    Returns:
        DbConnectionInfo: Named tuple containing parsed connection details.

    Raises:
        FileNotFoundError: If the specified config file doesn't exist.
        KeyError: If the sqlalchemy.url key is missing in the config.
        ValueError: If the URL parsing fails.
    """
    config = configparser.ConfigParser()
    config.read(config_path)

    if not config.has_option("alembic", "sqlalchemy.url"):
        raise KeyError("sqlalchemy.url not found in alembic.ini")

    raw_url = config.get("alembic", "sqlalchemy.url")
    parsed = urlparse(raw_url)

    if not all([parsed.scheme, parsed.path]):
        raise ValueError(f"Invalid database URL format: {raw_url}")

    # Extract components
    driver = parsed.scheme
    username = parsed.username or ""
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = str(parsed.port) if parsed.port else ""
    dbname = parsed.path.lstrip("/")

    return DbConnectionInfo(
        driver=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        dbname=dbname,
        full_url=raw_url.strip(),
    )


def get_db_url() -> str:
    """Get the database connection URL from alembic.ini configuration."""
    return get_alembic_db_info(file_util.get_file_path("alembic.ini")).full_url


def get_sqlite_db_path() -> str:
    """Get the absolute filesystem path for a SQLite database from the configured DB URL."""
    db_url = get_db_url()
    if db_url.strip() == "":
        raise ValueError("Invalid database URL")
    db_name = Path(db_url).name
    db_path = Path(file_util.get_resource_dir()) / "alembic" / "db" / db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{db_path.as_posix()}"


def get_db_dialect() -> str:
    """Get the database type from the configured SQLAlchemy URL in alembic.ini."""
    db_url = get_db_url()

    parsed = urlparse(db_url)
    if not parsed.scheme:
        raise ValueError(f"Invalid database URL: {db_url}")

    dialect = parsed.scheme.split("+")[0].lower()
    supported_dialects = {
        DBTypeEnum.PGSQL.value,
        DBTypeEnum.MYSQL.value,
        DBTypeEnum.SQLITE.value,
    }

    if dialect not in supported_dialects:
        raise ValueError(
            f"Unsupported database dialect: {dialect}. Supported: {', '.join(sorted(supported_dialects))}"
        )
    return dialect


def deep_merge_dict(
    base_dict: dict[str, Any], override_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge two dictionaries recursively.
    """
    if override_dict is None:
        return base_dict

    for key, value in override_dict.items():
        if (
            isinstance(value, dict)
            and key in base_dict
            and isinstance(base_dict[key], dict)
        ):
            base_dict[key] = deep_merge_dict(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict
