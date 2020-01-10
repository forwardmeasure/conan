FROM registry.access.redhat.com/ubi8/ubi:latest
#FROM us01vlhrbr0001.saas-n.com/cea/ubi8/ubi
  
ARG compute_engine_type=cpu
ARG cmake_version=3.19.2
ARG bazel_version=1.1.0

LABEL version="2.1.0" \
    description="Tensorflow C++ CUDA 10.2 Runtime Server"

RUN NVIDIA_GPGKEY_SUM=d1be581509378368edeec8c1eb2958702feedf3bc3d17011adbf24efacce4ab5 && \
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/7fa2af80.pub | sed '/^Version/d' > /etc/pki/rpm-gpg/RPM-GPG-KEY-NVIDIA && \
    echo "$NVIDIA_GPGKEY_SUM  /etc/pki/rpm-gpg/RPM-GPG-KEY-NVIDIA" | sha256sum -c --strict -

COPY cuda.repo /etc/yum.repos.d/cuda.repo

ENV CUDA_VERSION 10.2.89

ENV CUDA_PKG_VERSION 10-2-$CUDA_VERSION-1
# For libraries in the cuda-compat-* package: https://docs.nvidia.com/cuda/eula/index.html#attachment-a
RUN yum install -y \
	cuda-cudart-$CUDA_PKG_VERSION \
	cuda-compat-10-2 \
	cuda-nvml-dev-$CUDA_PKG_VERSION \
	cuda-command-line-tools-$CUDA_PKG_VERSION \
	cuda-libraries-dev-$CUDA_PKG_VERSION \
	cuda-minimal-build-$CUDA_PKG_VERSION \
	libcublas-devel-10.2.2.89-1 \
&& \
    ln -s cuda-10.2 /usr/local/cuda && \
    rm -rf /var/cache/yum/*

# nvidia-docker 1.0
RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=10.2 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411 brand=tesla,driver>=418,driver<419"
ENV LIBRARY_PATH /usr/local/cuda/lib64/stubs


ENV BT_BUILD_DIR=/opt/bt/build \
    BT_DOWNLOADS_DIR=/opt/bt/downloads \
    CONAN_USER_HOME=/opt/bt/conan \
    CMAKE_SCRIPT=install_cmake.py \
    BAZEL_SCRIPT=install_bazel.py \
    BAZEL_INSTALL_DIR=/opt/google/bazel \
    BTPA_CODE_HOME=/opt/bt/integration \
    CMAKE_INSTALL_DIR=/opt/cmake/${CMAKE_VERSION} \
    CONAN_BUILD_DIR=${BT_BUILD_DIR}/conan \
    COMPUTE_ENGINE_TYPE=$compute_engine_type \
    CMAKE_VERSION=$cmake_version \
    BAZEL_VERSION=$bazel_version

ENV PATH="$PATH:${CMAKE_INSTALL_DIR}/bin:${BAZEL_INSTALL_DIR}/bin"

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN dnf update -y; dnf clean all

RUN dnf -y upgrade && dnf install -y curl grep sed gcc gcc-c++ git wget unzip pkg-config autoconf libtool tar cpio patch file golang python36

# Download CMake
COPY ${CMAKE_SCRIPT} ${BAZEL_SCRIPT} ${BT_DOWNLOADS_DIR}/

RUN alternatives --set python /usr/bin/python3
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN pip3 install numpy conan;

RUN cd ${BT_DOWNLOADS_DIR} && python ./${CMAKE_SCRIPT} --cmake-version=${CMAKE_VERSION} --cmake-install-dir=${CMAKE_INSTALL_DIR}; \
    cd ${BT_DOWNLOADS_DIR} && python ./${BAZEL_SCRIPT} --bazel-version=${BAZEL_VERSION} --bazel-install-dir=${BAZEL_INSTALL_DIR};

COPY conan ${CONAN_BUILD_DIR}
RUN ${CONAN_BUILD_DIR}/conan_export_install.sh -e cuda
