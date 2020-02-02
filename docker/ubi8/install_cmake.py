#!/usr/bin/env python

import os
import platform
import logging
import argparse
import requests
import subprocess


def get_cmake_installer_file_name(version):
    uname = platform.system().lower().capitalize()
    arch = platform.machine()
    return "cmake-{}-{}-{}.tar.gz".format(version, uname, arch)


def get_cmake_download_location(version, installer_script):
    return "https://github.com/Kitware/CMake/releases/download/v{}/{}".format(version, installer_script)


def download_cmake(build_dir, file_name, download_url):
    os.chdir(build_dir)
    download_file = requests.get(download_url, allow_redirects=True)
    open(file_name, 'wb').write(download_file.content)


def install_cmake(build_dir, install_script, install_dir):
    os.chdir(build_dir)
    install_script_full = os.getcwd() + os.sep + install_script
    logging.info("[{}]".formatinstall_script_full)
    subprocess.run(["tar", "-zxvf", install_script_full, "-C", install_dir, "--strip-components=1"])


def configure_cmake_installer_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(description="Download and install Cmake")

    arg_parser.add_argument("--cmake-version",
                            help="The version of CMake you wish to install",
                            action="store",
                            dest="cmake_version",
                            required=True)
    arg_parser.add_argument("--cmake-install-dir",
                            help="The directory in which you want to install CMake",
                            action="store",
                            dest="cmake_install_dir",
                            required=True)
    arg_parser.add_argument("--cmake-build-dir",
                            help="The directory in which to download and install CMake",
                            action="store",
                            dest="cmake_build_dir",
                            default="/tmp/builds/CMake")
    return arg_parser


def download_and_install_cmake(version, build_dir, install_dir):
    logging.info("Installing CMake version {} in directory {}".format(version, build_dir))

    _installer_archive = get_cmake_installer_file_name(version)
    _download_url = get_cmake_download_location(version, _installer_archive)

    logging.info("Downloading {} from {}".format(_installer_archive, _download_url))

    os.makedirs(install_dir, mode=0o755, exist_ok=True)
    os.makedirs(build_dir, mode=0o755, exist_ok=True)

    download_cmake(build_dir, _installer_archive, _download_url)
    install_cmake(build_dir, _installer_archive, install_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_cmake_installer_arguments()
    cmd_line_args = parser.parse_args()
    download_and_install_cmake(cmd_line_args.cmake_version, cmd_line_args.cmake_build_dir, cmd_line_args.cmake_install_dir)
