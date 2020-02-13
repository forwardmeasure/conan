#!/usr/bin/env python

import os
import platform
import logging
import argparse
import requests
import subprocess

_nccl_sem_ver_version_map = {"2.5": "2.5.6"}
_nccl_version_archive_map = {"2.5.6": "nccl_2.5.6-2+cuda10.2_x86_64.txz"}


def configure_nccl_installer_arguments(arg_parser=None):
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(description="Download and install NCCL")

    arg_parser.add_argument(
        "--nccl-version",
        help="The version of nccl you wish to install",
        action="store",
        dest="nccl_version",
        required=True,
    )
    arg_parser.add_argument(
        "--nccl-install-dir",
        help="The directory in which you want to install nccl",
        action="store",
        dest="nccl_install_dir",
        required=True,
    )
    arg_parser.add_argument(
        "--nccl-build-dir",
        help="The directory in which to download and install nccl",
        action="store",
        dest="nccl_build_dir",
        default="/tmp/builds/nccl",
    )
    return arg_parser


def get_nccl_archive_file_name(version):
    return _nccl_version_archive_map[version]


def get_nccl_download_location(version):
    archive_name = get_nccl_archive_file_name(version)
    return (
        archive_name,
        "http://developer.download.nvidia.com/compute/redist/nccl/v{}/{}".format(version, archive_name),
    )


def download_nccl(build_dir, download_url):
    os.chdir(build_dir)
    download_cmd = "wget -q --show-progress --progress=bar:force {}".format(download_url)
    logging.info("Running {}".format(download_cmd))
    subprocess.Popen(["/bin/bash", "-c", download_cmd]).communicate()


# Install CUDNN. Note: to get updated download links for newer CUDA and CUDNN versions, go to the appropriate Dockerfile definition in DockerHub
# e.g. for CUDA 102 and CUDNN 7.6.5, go to https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/ubi8/10.2/devel/nccl7/Dockerfile
# RUN CUDNN_DOWNLOAD_SUM=600267f2caaed2fd58eb214ba669d8ea35f396a7d19b94822e6b36f9f7088c20 && \
#   curl -fsSL http://developer.download.nvidia.com/compute/redist/nccl/v${CUDNN_VERSION}/${CUDNN_ARCHIVE} -O && \
#   echo "$CUDNN_DOWNLOAD_SUM  ${CUDNN_ARCHIVE}" | sha256sum -c - && \
#   tar --no-same-owner -xzf ${CUDNN_ARCHIVE} --strip-components 1 -C ${CUDNN_HOME} && \
#   rm ${CUDNN_ARCHIVE} && \
#   ldconfig


def install_nccl(build_dir, archive_name, install_dir):
    os.chdir(build_dir)
    install_cmd = "tar -xvf {} --strip-components 1 -C {}".format(os.path.join(os.getcwd(), archive_name), install_dir)
    logging.info("Running {}".format(install_cmd))
    subprocess.Popen(["/bin/bash", "-c", install_cmd]).communicate()


def download_and_install_nccl(version, build_dir, install_dir):
    logging.info("Installing nccl version {} in directory {}".format(_nccl_sem_ver_version_map[version], build_dir))

    (installer, download_url) = get_nccl_download_location(_nccl_sem_ver_version_map[version])

    os.makedirs(install_dir, mode=0o755, exist_ok=True)
    os.makedirs(build_dir, mode=0o755, exist_ok=True)

    download_nccl(build_dir, download_url)
    install_nccl(build_dir, installer, install_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = configure_nccl_installer_arguments()
    cmd_line_args = parser.parse_args()
    download_and_install_nccl(
        cmd_line_args.nccl_version, cmd_line_args.nccl_build_dir, cmd_line_args.nccl_install_dir
    )
