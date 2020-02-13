#!/usr/bin/env python

import os
import platform
import logging
import argparse
import requests
import subprocess

_cudnn_sem_ver_version_map = {"7.6": "7.6.5"}
_cudnn_version_archive_map = {"7.6.5": "cudnn-10.2-linux-x64-v7.6.5.32.tgz"}


def configure_cudnn_installer_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(description="Download and install CUDNN")

    arg_parser.add_argument(
        "--cudnn-version",
        help="The version of cudnn you wish to install",
        action="store",
        dest="cudnn_version",
        required=True,
    )
    arg_parser.add_argument(
        "--cudnn-install-dir",
        help="The directory in which you want to install cudnn",
        action="store",
        dest="cudnn_install_dir",
        required=True,
    )
    arg_parser.add_argument(
        "--cudnn-build-dir",
        help="The directory in which to download and install cudnn",
        action="store",
        dest="cudnn_build_dir",
        default="/tmp/builds/cudnn",
    )
    return arg_parser


def get_cudnn_archive_file_name(version):
    return _cudnn_version_archive_map[version]


def get_cudnn_download_location(version):
    archive_name = get_cudnn_archive_file_name(version)
    return (
        archive_name,
        "http://developer.download.nvidia.com/compute/redist/cudnn/v{}/{}".format(version, archive_name),
    )


def download_cudnn(build_dir, download_url):
    os.chdir(build_dir)
    download_cmd = "wget -q --show-progress --progress=bar:force {}".format(download_url)
    logging.info("Running {}".format(download_cmd))
    subprocess.Popen(["/bin/bash", "-c", download_cmd]).communicate()


# Install CUDNN. Note: to get updated download links for newer CUDA and CUDNN versions, go to the appropriate Dockerfile definition in DockerHub
# e.g. for CUDA 102 and CUDNN 7.6.5, go to https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/ubi8/10.2/devel/cudnn7/Dockerfile
# RUN CUDNN_DOWNLOAD_SUM=600267f2caaed2fd58eb214ba669d8ea35f396a7d19b94822e6b36f9f7088c20 && \
#   curl -fsSL http://developer.download.nvidia.com/compute/redist/cudnn/v${CUDNN_VERSION}/${CUDNN_ARCHIVE} -O && \
#   echo "$CUDNN_DOWNLOAD_SUM  ${CUDNN_ARCHIVE}" | sha256sum -c - && \
#   tar --no-same-owner -xzf ${CUDNN_ARCHIVE} --strip-components 1 -C ${CUDNN_HOME} && \
#   rm ${CUDNN_ARCHIVE} && \
#   ldconfig


def install_cudnn(build_dir, archive_name, install_dir):
    os.chdir(build_dir)
    install_cmd = "tar -zxvf {} --strip-components 1 -C {}".format(os.path.join(os.getcwd(), archive_name), install_dir)
    logging.info("Running {}".format(install_cmd))
    subprocess.Popen(["/bin/bash", "-c", install_cmd]).communicate()


def download_and_install_cudnn(version, build_dir, install_dir):
    logging.info("Installing cudnn version {} in directory {}".format(_cudnn_sem_ver_version_map[version], build_dir))

    (installer, download_url) = get_cudnn_download_location(_cudnn_sem_ver_version_map[version])

    os.makedirs(install_dir, mode=0o755, exist_ok=True)
    os.makedirs(build_dir, mode=0o755, exist_ok=True)

    download_cudnn(build_dir, download_url)
    install_cudnn(build_dir, installer, install_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_cudnn_installer_arguments()
    cmd_line_args = parser.parse_args()
    download_and_install_cudnn(
        cmd_line_args.cudnn_version, cmd_line_args.cudnn_build_dir, cmd_line_args.cudnn_install_dir
    )
