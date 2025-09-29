# SPDX-License-Identifier: MIT
"""Routing of the application.

Automatically discovers and includes all controller routers from the controller directory.
Each controller file should be named '*_controller.py' and contain a corresponding '*_router' variable.
Supports recursive directory traversal.
"""

import importlib
import os
import traceback
from pathlib import Path

from fastapi import APIRouter
from loguru import logger

from fastlib.utils import str_util


def register_router(
    controller_dirs: list[str] = None,
    controller_flag: str = "controller",
    router_flag: str = "router",
    remove_prefix_set: set[str] = None,
    api_version: str = "/v1",
    module_base_prefix: str = "src",
    module_separator: str = ".",
    controller_file_pattern_template: str = "*_{}.py",
) -> APIRouter:
    """Register routers recursively from controller directories.

    Args:
        controller_dirs: List of directories to search for controllers
        controller_flag: Suffix to identify controller files (e.g. 'controller' for '*_controller.py')
        router_flag: Suffix to identify router variables (e.g. 'router' for '*_router')
        remove_prefix_set: set of prefixes to remove from router names
        api_version: API version prefix (e.g. '/v1')
        module_base_prefix: Base prefix for module imports
        module_separator: Separator for module paths
        controller_file_pattern_template: Template for controller file pattern

    Returns:
        APIRouter with all discovered routes registered
    """
    if controller_dirs is None:
        controller_dirs = []
    if remove_prefix_set is None:
        remove_prefix_set = {"sys"}

    router = APIRouter()

    def process_directory(directory: Path):
        """Recursively process a directory to find controller files."""
        for item in directory.iterdir():
            if item.is_dir():
                # If it's a directory, recursively process it
                process_directory(item)
            elif item.is_file() and item.name.endswith(f"_{controller_flag}.py"):
                # Process controller files
                process_controller_file(item)

    def process_controller_file(controller_file: Path):
        """Process a single controller file and register its router."""
        module_name = controller_file.stem
        if "field_controller" in module_name:
            pass
        # Calculate relative path from module_base_prefix
        try:
            relative_path = str(controller_file).split(module_base_prefix)[1]
        except ValueError:
            # If the file is not under module_base_prefix, use its absolute path
            relative_path = str(controller_file)

        # Convert path to module path (replace separators and remove .py)
        module_path = (
            relative_path.replace(".py", "")
            .replace("/", module_separator)
            .replace(os.sep, module_separator)
            .lstrip(".")
        )

        # Ensure the path starts from the base prefix
        if not module_path.startswith(module_base_prefix):
            module_path = f"{module_base_prefix}.{module_path}"

        try:
            module = importlib.import_module(module_path)
            router_var_name = module_name.replace(controller_flag, router_flag)
            for remove_prefix in remove_prefix_set:
                router_var_name = router_var_name.replace(f"{remove_prefix}_", "")

            if hasattr(module, router_var_name):
                prefix = f"/{module_name.replace(f'_{controller_flag}', '')}"
                for remove_prefix in remove_prefix_set:
                    prefix = prefix.replace(f"{remove_prefix}_", "").replace("_", "-")
                router_instance = getattr(module, router_var_name)
                router.include_router(
                    router_instance,
                    tags=[
                        str_util.snake_to_title(
                            module_name.replace(f"_{controller_flag}", "")
                        )
                    ],
                    prefix=f"{api_version}",
                )
        except ImportError as e:
            logger.error(f"Failed to import {module_path}: {e}")
            traceback.print_stack()
            raise SystemError(f"Failed to import {module_path}: {e}") from e

    for controller_item in controller_dirs:
        controller_dir = Path(controller_item).resolve()
        if controller_dir.is_dir():
            process_directory(controller_dir)
        elif controller_dir.is_file() and controller_dir.name.endswith(
            f"_{controller_flag}.py"
        ):
            # Also allow directly specifying controller files
            process_controller_file(controller_dir)
        else:
            logger.warning(
                f"Path {controller_dir} is neither a directory nor a valid controller file"
            )

    return router
