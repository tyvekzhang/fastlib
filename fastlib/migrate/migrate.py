# SPDX-License-Identifier: MIT
"""Use when performing database migration"""

import importlib
from pathlib import Path
from typing import Optional

from loguru import logger

current_path = Path(__file__).resolve()
src_parent = None

for parent in current_path.parents:
    if parent.name == "src":
        src_parent = parent.parent
        break

if not src_parent:
    raise FileNotFoundError("Can not found src dir")

model_path = src_parent / "src" / "main" / "app" / "model"

# List of directories to scan for model files
MODEL_PACKAGES = [model_path]


def import_sql_models(packages: Optional[list[Path]] = None) -> dict[str, type]:
    packages_to_scan = packages or MODEL_PACKAGES
    imported_models = {}

    for package_dir in packages_to_scan:
        if not package_dir.exists():
            logger.warning(f"Package directory not found: {package_dir}")
            continue

        for model_file in package_dir.glob("*_model.py"):
            relative_path = model_file.relative_to(src_parent)
            module_path = ".".join(relative_path.with_suffix("").parts)

            try:
                module = importlib.import_module(module_path)
                for name in dir(module):
                    if name.endswith("Model"):
                        imported_models[name] = getattr(module, name)

            except ImportError as e:
                logger.error(f"Failed to import {module_path}: {e}")
            except Exception:
                logger.exception(f"Error processing {model_file}")

    return imported_models


# Import models from default packages
import_sql_models()

# Alternatively, import from specific packages:
# imported_models = import_models(["custom/package/models", "another/package/models"])

# For Alembic startup
ALEMBIC_START_SIGNAL = "Welcome! autogenerate is processing!"
