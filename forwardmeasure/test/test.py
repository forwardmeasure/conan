#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path
sys.executable

import forwardmeasure
from forwardmeasure.utils import ConfigUtils

if __name__ == "__main__":
    sys.path
    sys.executable

    x = forwardmeasure.utils.ConfigUtils()

    config_utils = ConfigUtils()

    try:
        CFG_FILE_NAME = "config.ini"
        my_config = config_utils.read_config(CFG_FILE_NAME)
        name = my_config["PACKAGE"]["name"]
        version = my_config["PACKAGE"]["version"]
        dependencies = my_config["DEPENDENCIES"]
    except Exception as ex:
        print("Exception occurred: " + str(ex))

    print(__name__)
