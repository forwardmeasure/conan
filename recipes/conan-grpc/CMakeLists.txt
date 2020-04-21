cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

message ("Building gRPC: CMAKE_SOURCE_DIR = ${CMAKE_SOURCE_DIR},  CMAKE_BINARY_DIR = ${CMAKE_BINARY_DIR}")

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake)
message ("CMAKE_MODULE_PATH = ${CMAKE_MODULE_PATH}")

list(APPEND CMAKE_PREFIX_PATH ${CONAN_ABSL_ROOT})
message ("CMAKE_PREFIX_PATH = ${CMAKE_PREFIX_PATH}")

set(ABSL_ROOT ${CONAN_ABSL_ROOT})

add_subdirectory("source_subfolder")
