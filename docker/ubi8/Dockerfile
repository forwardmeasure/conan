FROM us01vlhrbr0001.saas-n.com/cea/ubi8/ubi

ARG compute_engine_type=cpu
ARG cmake_version=3.19.2
ARG bazel_version=1.1.0

LABEL version="2.1.0" \
    description="Tensorflow C++ CPU Runtime Server"

RUN echo "Oh dang look at that $cmake_version"

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

COPY entrypoint.sh /opt/

EXPOSE 8080 8081
#ENTRYPOINT [ "/opt/entrypoint.sh" ]
