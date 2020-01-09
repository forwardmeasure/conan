#!/usr/bin/env python

import os
import platform
import logging
import argparse
import requests
import subprocess


def get_bazel_installer_file_name(version):
    uname = platform.system().lower()
    arch = platform.machine()
    return "bazel-%s-installer-%s-%s.sh" % (version, uname, arch)


def get_bazel_download_location(version, installer_script):
    return "https://github.com/bazelbuild/bazel/releases/download/%s/%s" % (version, installer_script)


def download_bazel(build_dir, file_name, download_url):
    os.chdir(build_dir)
    download_file = requests.get(download_url, allow_redirects=True)
    open(file_name, 'wb').write(download_file.content)


def install_bazel(build_dir, install_script, install_dir):
    os.chdir(build_dir)
    install_script_full = os.getcwd() + os.sep + install_script
    os.chmod(install_script_full, 0o744)
    subprocess.run([install_script_full, "--prefix=%s" % install_dir])


def configure_bazel_installer_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(description="Download and install Bazel")

    arg_parser.add_argument("--bazel-version",
                            help="The version of Bazel you wish to install",
                            action="store",
                            dest="bazel_version",
                            required=True)
    arg_parser.add_argument("--bazel-install-dir",
                            help="The directory in which you want to install Bazel",
                            action="store",
                            dest="bazel_install_dir",
                            required=True)
    arg_parser.add_argument("--bazel-build-dir",
                            help="The directory in which to download and build Bazel",
                            action="store",
                            dest="bazel_build_dir",
                            default="/tmp/builds/bazel")
    return arg_parser


def download_and_install_bazel(version, build_dir, install_dir):
    _installer_script = get_bazel_installer_file_name(version)
    _download_url = get_bazel_download_location(version, _installer_script)

    logging.info("Downloading %s from %s" % (_installer_script, _download_url))

    os.makedirs(install_dir, mode=0o755, exist_ok=True)
    os.makedirs(build_dir, mode=0o755, exist_ok=True)

    download_bazel(build_dir, _installer_script, _download_url)

    logging.info("Installing Bazel version %s in directory %s" % (version, build_dir))
    install_bazel(build_dir, _installer_script, install_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_bazel_installer_arguments()
    cmd_line_args = parser.parse_args()
    download_and_install_bazel(cmd_line_args.bazel_version, cmd_line_args.bazel_build_dir, cmd_line_args.bazel_install_dir)
