project(conanzlib)
cmake_minimum_required(VERSION 2.8)

include(conanbuildinfo.cmake)

conan_basic_setup(KEEP_RPATHS)

include_directories(${CMAKE_SOURCE_DIR}/sources)
add_subdirectory("${CMAKE_SOURCE_DIR}/sources")
