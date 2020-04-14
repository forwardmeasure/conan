#!/bin/bash

export CUDA_VERSION=10.2.89
export CUDA_PKG_VERSION="10-2=$CUDA_VERSION-1"
export CUDNN_VERSION=7.6.5.32
export NCCL_VERSION=2.6.4

apt-get update && apt-get install -y --no-install-recommends \
		gnupg2 curl ca-certificates && \
    	curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | apt-key add - && \
    	echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    	echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list 

# For libraries in the cuda-compat-* package: https://docs.nvidia.com/cuda/eula/index.html#attachment-a
apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-$CUDA_PKG_VERSION \
		cuda-compat-10-2 && \
		ln -s cuda-10.2 /usr/local/cuda && 

apt-get update && apt-get install -y --no-install-recommends \
    	pciutils lshw \
    	cuda-libraries-$CUDA_PKG_VERSION \
    	cuda-nvtx-$CUDA_PKG_VERSION \
    	libcublas10-10.2.2.89-1 \
    	libnccl-2.6.4-1+cuda10.2 \
    	libcudnn7-7.6.5.33-1.cuda10.2 \
    	libnvinfer7 libnvparsers7 libnvonnxparsers7 libnvinfer-plugin7

# Required for nvidia-docker v1
echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

export PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64

apt-get update && apt-get install -y --no-install-recommends \
    	cuda-nvml-dev-$CUDA_PKG_VERSION \
    	cuda-command-line-tools-$CUDA_PKG_VERSION \
		cuda-libraries-dev-$CUDA_PKG_VERSION \
		cuda-minimal-build-$CUDA_PKG_VERSION \
    	libcudnn7=$CUDNN_VERSION-1+cuda10.2 \
    	libcudnn7-dev=$CUDNN_VERSION-1+cuda10.2 \
		libnccl-dev=$NCCL_VERSION-1+cuda10.2 \
		libcublas-dev=10.2.2.89-1 \
        libnvinfer-dev libnvparsers-dev libnvonnxparsers-dev libnvinfer-plugin-dev \
	&& \
    	apt-mark hold libcudnn7 && \
		apt-mark hold libnccl2

export LIBRARY_PATH=${LIBRARY_PATH}:/usr/local/cuda/lib64/stubs

# nvidia-container-runtime
export NVIDIA_VISIBLE_DEVICES=all
export NVIDIA_DRIVER_CAPABILITIES="compute,utility"
export NVIDIA_REQUIRE_CUDA="cuda>=10.2 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411 brand=tesla,driver>=418,driver<419"

export CUDA_HOME=/usr/local/cuda
export PATH=/usr/local/cuda/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64
export LIBRARY_PATH=${LIBRARY_PATH:+${LIBRARY_PATH}:}/usr/local/cuda/lib64/stubs
