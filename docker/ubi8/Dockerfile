FROM registry.access.redhat.com/ubi8/ubi:latest

ARG compute_engine_type=cpu
ARG cmake_version=3.16.2
ARG bazel_version=1.1.0
ARG cuda_version=10.2
ARG cudnn_version=7.6
ARG nccl_version=2.5

LABEL version="1.0.0" \
    description="Tensorflow C++ CUDA 10.2 Runtime Server"

ENV CONAN_USER_HOME=/opt/conan \
    SW_BUILD_DIR=/opt/software/build \
    SW_DOWNLOADS_DIR=/opt/software/downloads \
    CMAKE_SCRIPT=install_cmake.py \
    BAZEL_SCRIPT=install_bazel.py \
    CUDA_TOOLKIT_SCRIPT=install_cuda_toolkit.py \
    CUDNN_SCRIPT=install_cudnn.py \
    NCCL_SCRIPT=install_nccl.py \
    COMPUTE_ENGINE_TYPE=$compute_engine_type \
    CMAKE_VERSION=$cmake_version \
    BAZEL_VERSION=$bazel_version \
    CUDA_VERSION=$cuda_version \
    CUDNN_VERSION=$cudnn_version \
    NCCL_VERSION=$nccl_version

ENV CMAKE_INSTALL_DIR=/opt/cmake/${CMAKE_VERSION} \
    BAZEL_INSTALL_DIR=/opt/google/bazel/${BAZEL_VERSION} \
    CUDA_HOME=/opt/nvidia/cuda-${CUDA_VERSION} \
    CUDNN_HOME=/opt/nvidia/cudnn-${CUDNN_VERSION} \
    NCCL_HOME=/opt/nvidia/nccl-${NCCL_VERSION} \
    CONAN_BUILD_DIR=${SW_BUILD_DIR}/conan
ENV PATH="$PATH:${CMAKE_INSTALL_DIR}/bin:${BAZEL_INSTALL_DIR}/bin"

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN dnf update -y; dnf clean all; dnf -y upgrade && \
    dnf install -y curl grep sed gcc gcc-c++ git wget unzip pkg-config \
    autoconf libtool tar cpio patch file golang glibc-langpack-en python36

RUN mkdir -p ${SW_DOWNLOADS_DIR} ${CUDA_HOME} ${CUDNN_HOME}

# Download CMake and Bazel installers
COPY ${CMAKE_SCRIPT} ${BAZEL_SCRIPT} ${CUDA_TOOLKIT_SCRIPT} ${CUDNN_SCRIPT} ${SW_DOWNLOADS_DIR}/

RUN alternatives --set python /usr/bin/python3
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
RUN pip install numpy conan;

#Install CMake
RUN cd ${SW_DOWNLOADS_DIR} && python ./${CMAKE_SCRIPT} --cmake-version=${CMAKE_VERSION} \
    --cmake-install-dir=${CMAKE_INSTALL_DIR} \
    --cmake-build-dir=${SW_BUILD_DIR}/cmake

#Install Bazel
RUN cd ${SW_DOWNLOADS_DIR} && python ./${BAZEL_SCRIPT} --bazel-version=${BAZEL_VERSION} \
    --bazel-install-dir=${BAZEL_INSTALL_DIR} \
    --bazel-build-dir=${SW_BUILD_DIR}/bazel

# Install CUDA
RUN cd ${SW_DOWNLOADS_DIR} && python ./${CUDA_TOOLKIT_SCRIPT} --cuda-version=${CUDA_VERSION} \
    --cuda-install-dir=${CUDA_HOME} \
    --cuda-build-dir=${SW_BUILD_DIR}/cuda

# Install CUDNN
RUN cd ${SW_DOWNLOADS_DIR} && python ./${CUDNN_SCRIPT} --cudnn-version=${CUDNN_VERSION} \
    --cudnn-install-dir=${CUDNN_HOME} \

# Install NCCL
RUN cd ${SW_DOWNLOADS_DIR} && python ./${NCCL_SCRIPT} --nccl-version=${NCCL_VERSION} \
    --nccl-install-dir=${NCCL_HOME} \
    --nccl-build-dir=${SW_BUILD_DIR}/nccl

RUN echo "${CUDA_HOME}/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH ${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH ${CUDA_HOME}/lib64:${CUDNN_HOME}/lib64

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=10.2 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411 brand=tesla,driver>=418,driver<419"

#COPY conan ${CONAN_BUILD_DIR}
#RUN ${CONAN_BUILD_DIR}/conan_export_install.sh -e ${COMPUTE_ENGINE_TYPE}
