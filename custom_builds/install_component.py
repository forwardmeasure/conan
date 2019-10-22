#!/usr/bin/env python

import os
import platform
import subprocess
import logging
import argparse
import requests
import subprocess

from forwardmeasure.utils import ConfigUtils


def configure_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(
            description="Download and install Cmake")

    arg_parser.add_argument(
        "--component-dir",
        help="The directory of the component you wish to install",
        action="store",
        dest="component_dir",
        required=True)

    arg_parser.add_argument(
        "--install-dir",
        help=
        "The directory in which you want to install the Conan config artefacts",
        action="store",
        dest="install_dir",
        required=True)

    arg_parser.add_argument(
        "--install-channel",
        help=
        "The Conan channel to which you want to install the Conan component",
        action="store",
        dest="install_channel",
        default="forwardmeasure/stable")

    return arg_parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_arguments()
    cmd_line_args = parser.parse_args()

    # Change to the directory and read the config file
    config_file_path = cmd_line_args.component_dir + os.sep + "config.ini"
    logging.info("Opening config %s" % (config_file_path))

    config = ConfigUtils().read_config(config_file_path)

    name = config["PACKAGE"]["name"]
    version = config["PACKAGE"]["version"]
    channel = cmd_line_args.install_channel

    logging.info("Exporting component %s, version %s, channel %s" %
                 (name, version, channel))

    # Export the conan script
    subprocess.run(["conan", "export", cmd_line_args.component_dir, channel])

    package_spec = name + "/" + version + "@" + channel
    logging.info("Importing component %s" % package_spec)

    subprocess.run(["conan", "install", "--build", name, package_spec])
