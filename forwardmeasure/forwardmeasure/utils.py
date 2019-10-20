import sys
import os
import logging
import argparse
import subprocess
import configparser
import re

from conans import ConanFile
from conans.tools import load


class EnvInterpolation(configparser.ExtendedInterpolation):
    """Interpolation class that expands environment variables in values."""
    def before_get(self, parser, section, option, value, defaults):
        ret_val = super().before_get(parser, section, option,
                                     os.path.expandvars(value), defaults)
        return ret_val


class ConfigUtils:
    def __init__(self):
        self._config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())

    def read_config(self, config_file):
        """
        Parse a config file for properies such as versions.

        Parameters
        ---------
        config_file: Argument bundle
        """

        logging.info('Reading configuration from %s' % (config_file))
        self._config.read(config_file)

        return self._config


class CmakeUtils:
    def get_name(self):
        try:
            content = load("CMakeLists.txt")
            name = re.search(b"project\((.*)\)", content).group(1)
            return name.strip()
        except Exception as e:
            return None

    def get_version(self):
        try:
            content = load("CMakeLists.txt")
            version = re.search(b"set\(LIBRARY_VERSION (.*)\)",
                                content).group(1)
            return version.strip()
        except Exception as e:
            return None
