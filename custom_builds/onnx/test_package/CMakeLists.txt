cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(onnx_hello onnx_hello.cpp)
target_link_libraries(onnx_hello ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME onnx_hello
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND onnx_hello)
