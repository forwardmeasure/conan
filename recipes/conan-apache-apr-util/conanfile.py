#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake
import os

class ApacheAPRUtil(ConanFile):
    name = "apache-apr-util"
    version = "1.6.1"
    url = "https://github.com/forwardmeasure/conan-apache-apr-util"
    homepage = "https://apr.apache.org/"
    license = "http://www.apache.org/LICENSE.txt"
    description = "The mission of the Apache Portable Runtime (APR) project is to create and maintain " \
                  "software libraries that provide a predictable and consistent interface to underlying " \
                  "platform-specific implementations."
    exports_sources = ["LICENSE", ]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    lib_name = "apr-util-" + version

    def configure(self):
        del self.settings.compiler.libcxx  # It is a C library

    def requirements(self):
        self.requires("apache-apr/1.7.0@forwardmeasure/stable")
        self.requires("expat/2.2.6@forwardmeasure/stable")

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-util-{v}{ext}".format(v=self.version, ext=file_ext))

    def patch(self):
        tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                              "PROJECT(APR-Util C)",
                              """
                              PROJECT(APR-Util C)
                              include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                              conan_basic_setup()
                              """)

        # Fix a ¿bug? Maybe it has changed in FindExpat module
        tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                              "SET(XMLLIB_INCLUDE_DIR   ${EXPAT_INCLUDE_DIRS})",
                              "SET(XMLLIB_INCLUDE_DIR   ${EXPAT_INCLUDE_DIR})")
        tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                              "SET(XMLLIB_LIBRARIES     ${EXPAT_LIBRARIES})",
                              "SET(XMLLIB_LIBRARIES     ${EXPAT_LIBRARY})")

        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/",
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/bin/")
                tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),  # TODO: Do not make it optional, grab the files and copy them.
                                      "          CONFIGURATIONS RelWithDebInfo Debug)",
                                      "          CONFIGURATIONS RelWithDebInfo Debug OPTIONAL)")

    def build(self):
        self.patch()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.definitions["APR_INCLUDE_DIR"] = self.deps_cpp_info["apache-apr"].include_paths[0]
            cmake.definitions["APR_LIBRARIES"] = os.path.join(self.deps_cpp_info["apache-apr"].lib_paths[0], "libapr-1.lib")
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            args = ['--prefix', self.package_folder,
                    '--with-apr={}'.format(self.deps_cpp_info["apache-apr"].rootpath),
                    '--with-expat={}'.format(self.deps_cpp_info["expat"].rootpath),
                    ]
            env_build.configure(configure_dir=self.lib_name,
                                args=args,
                                host=self.settings.arch,
                                build=False)  # TODO: Workaround for https://github.com/conan-io/conan/issues/2552
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        # TODO: Copy files from apache-apr, this project expected them side by side
        # self.copy("*.h", dst="include", src=os.path.join(self.deps_cpp_info["apache-apr"].include_paths[0]))
        self.copy("LICENSE", src=self.lib_name)

    def package_id(self):
        self.info.options.shared = "Any"  # Both, shared and static are built always

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                libs = ["libaprutil-1", ]
            else:
                libs = ["aprutil-1", "ws2_32", "Rpcrt4", ]
                self.cpp_info.defines = ["APU_DECLARE_STATIC", ]
        else:
            libs = ["aprutil-1", ]
            if not self.options.shared:
                libs += ["pthread", ]
            self.cpp_info.includedirs = [os.path.join("include", "apr-1"), ]
        self.cpp_info.libs = libs
