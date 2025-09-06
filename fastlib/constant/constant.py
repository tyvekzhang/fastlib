# SPDX-License-Identifier: MIT
"""Common constant"""

import os

current_dir: str = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR: str = os.path.abspath(
    os.path.join(current_dir, os.pardir, os.pardir, os.pardir, "resource")
)

ADMIN_ID = 9
ROOT_PARENT_ID = 0
MAX_PAGE_SIZE = 1000

ENV = "env"
PARENT_ID = "parent_id"
CONFIG_FILE = "config_file"
CONFIG_FILE_NAME = "config.yml"
AUTHORIZATION = "Authorization"


class FilterOperators:
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    GE = "GE"
    LT = "LT"
    LE = "LE"
    BETWEEN = "BETWEEN"
    LIKE = "LIKE"
