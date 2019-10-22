import sys
import os

from conans import ConanFile
from conans.tools import load

from forwardmeasure.utils import ConfigUtils


class ConfigurableConanFile(ConanFile):
    """Enables external configuration of Conan recipes"""
    def init_conan_config_params():
        cfg_file_name = "config.ini"
        my_config = ConfigUtils().read_config(cfg_file_name)

        name = my_config["PACKAGE"]["name"]
        version = my_config["PACKAGE"]["version"]
        dependencies = my_config["DEPENDENCIES"]
        exports = ["config.ini"]

        return (name, version, dependencies, exports)
