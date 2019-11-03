import sys
import os
import json
import re

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
    
    def parseConanPackageSpec(spec):
        match = re.search(r'([\w.-]+)/([\w.-]+)@([\w.-]+)/([\w.-]+)', spec)
        if match:
            all = match.group()
            package = match.group(1)
            version = match.group(2)
            user = match.group(3)
            channel = match.group(4)
        else:
            print ("Unable to match")
    
        return (package, version, user, channel);
    
    def buildConanPackageSpec(package, version, user, channel):
        return package + "/" + version + "@" + user + "/" + channel
