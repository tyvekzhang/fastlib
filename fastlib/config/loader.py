# SPDX-License-Identifier: MIT
"""ConfigLoader class for loading and managing application configurations from YAML files."""

import os
from typing import Any, Optional

import yaml
from loguru import logger

from fastlib import constant
from fastlib.config import utils as config_util


class ConfigLoader:
    def __init__(self, env: str, base_config_file: Optional[str] = None) -> None:
        """
        Initializes a new instance of the ConfigLoader class

        Args:
            env (str): The environment (e.g., 'dev', 'prod')
            base_config_file (str, optional): The base config file path
        """
        self.env = env
        self.default_flag = base_config_file is None

        if base_config_file is None:
            self.base_config_file = os.path.join(
                constant.RESOURCE_DIR, constant.CONFIG_FILE_NAME
            )
        else:
            self.base_config_file = base_config_file

        self.config: dict[str, Any] = {}

    @staticmethod
    def load_yaml_file(file_path: str) -> dict[str, Any]:
        """
        Load a YAML file and return its contents as a dictionary.

        Args:
            file_path (str): The path to the YAML file to be loaded.

        Returns:
            dict: The contents of the YAML file as a dictionary.

        Raises:
            FileNotFoundError: If the file does not exist
            yaml.YAMLError: If there is an error parsing the YAML
        """
        if not os.path.exists(file_path):
            logger.warning(
                f"Config file not found: {file_path}, will use the default config"
            )
            return {}

        with open(file_path, encoding="utf-8") as file:
            try:
                return yaml.safe_load(file) or {}
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {e}") from e

    def load_config(self, environment: Optional[str] = None) -> dict[str, Any]:
        """
        Load the base configuration and merge with environment-specific settings.
        """
        target_env = environment or self.env
        if not target_env:
            raise ValueError("Environment must be specified")

        # Load base config
        self.config = self.load_yaml_file(self.base_config_file)

        # Always try to load environment-specific config if it exists
        base_dir = os.path.dirname(self.base_config_file)
        base_filename = os.path.basename(self.base_config_file)
        env_config_file = base_filename.replace(".", f"-{target_env}.")
        env_config_path = os.path.join(base_dir, env_config_file)

        if os.path.exists(env_config_path):
            env_config = self.load_yaml_file(env_config_path)
            self.config = config_util.deep_merge_dict(
                base_dict=self.config, override_dict=env_config
            )

        return self.config
