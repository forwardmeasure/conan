project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(mxnet_test mxnet_test.cpp)
target_link_libraries(mxnet_test ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
enable_testing()
add_test(NAME mxnet_test
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
         COMMAND example)
