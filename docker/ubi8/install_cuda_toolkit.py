#!/usr/bin/env python

import os
import platform
import logging
import argparse
import requests
import subprocess

_cuda_version_installer_map = {"10.2": "cuda_10.2.89_440.33.01_linux.run"}


def configure_cuda_installer_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(description="Download and install CUDA")

    arg_parser.add_argument(
        "--cuda-version",
        help="The version of cuda you wish to install",
        action="store",
        dest="cuda_version",
        required=True,
    )
    arg_parser.add_argument(
        "--cuda-install-dir",
        help="The directory in which you want to install cuda",
        action="store",
        dest="cuda_install_dir",
        required=True,
    )
    arg_parser.add_argument(
        "--cuda-build-dir",
        help="The directory in which to download and install cuda",
        action="store",
        dest="cuda_build_dir",
        default="/tmp/builds/cuda",
    )

    return arg_parser


def get_cuda_installer_file_name(version):
    return _cuda_version_installer_map[version]


def get_cuda_download_location(version):
    installer = get_cuda_installer_file_name(version)
    return (
        installer,
        "http://developer.download.nvidia.com/compute/cuda/{}/Prod/local_installers/{}".format(version, installer),
    )


def download_cuda(build_dir, download_url):
    download_cmd = "cd {} && wget -q --show-progress --progress=bar:force {}".format(build_dir, download_url)
    logging.info("Running {}".format(download_cmd))
    subprocess.Popen(["/bin/bash", "-c", download_cmd]).communicate()


def install_cuda(build_dir, install_script, install_dir):
    os.chdir(build_dir)
    install_cmd = "cd {} && bash {} --override --no-opengl-libs --silent --toolkit --toolkitpath={} --defaultroot={}".format(
        build_dir, os.path.join(os.getcwd(), install_script), install_dir, install_dir
    )
    logging.info("Running {}".format(install_cmd))
    subprocess.Popen(["/bin/bash", "-c", install_cmd]).communicate()


def download_and_install_cuda(version, build_dir, install_dir):
    logging.info("Installing cuda version {} in directory {}".format(version, install_dir))

    (installer, download_url) = get_cuda_download_location(version)

    os.makedirs(install_dir, mode=0o755, exist_ok=True)
    os.makedirs(build_dir, mode=0o755, exist_ok=True)

    download_cuda(build_dir, download_url)
    install_cuda(build_dir, installer, install_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_cuda_installer_arguments()
    cmd_line_args = parser.parse_args()
    download_and_install_cuda(cmd_line_args.cuda_version, cmd_line_args.cuda_build_dir, cmd_line_args.cuda_install_dir)
