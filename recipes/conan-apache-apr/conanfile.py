#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake

import os
import glob

class ApacheAPR(ConanFile):
    name = "apache-apr"
    version = "1.7.0"
    homepage = "https://apr.apache.org/"
    license = "http://www.apache.org/LICENSE.txt"
    description = "The mission of the Apache Portable Runtime (APR) project is to create and maintain " \
                  "software libraries that provide a predictable and consistent interface to underlying " \
                  "platform-specific implementations."
    exports_sources = ["LICENSE", ]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    lib_name = "apr-" + version

    def configure(self):
        del self.settings.compiler.libcxx  # It is a C library

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-{v}{ext}".format(v=self.version, ext=file_ext))

    def patch(self):
        if self.settings.os == "Windows":
            tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                  "# Generated .h files are stored in PROJECT_BINARY_DIR, not the",
                                  """
                                  include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                  conan_basic_setup()
                                  # Generated .h files are stored in PROJECT_BINARY_DIR, not the
                                  """)

            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/libapr-1.pdb)",
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/bin/libapr-1.pdb)")

    def build(self):
        self.patch()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            env_build.configure(configure_dir=self.lib_name, args=['--prefix', self.package_folder, ], build=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy("LICENSE", src=self.lib_name)

        # And I modify deployed folder a little bit given config options (needed in Mac to link against desired libs)
        if self.options.shared:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.a")):
                os.remove(f)
        else:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.dylib")):
                os.remove(f)
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.so*")):
                os.remove(f)
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(f)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                libs = ["libapr-1", "libaprapp-1", ]
            else:
                libs = ["apr-1", "aprapp-1", "ws2_32", "Rpcrt4", ]
                self.cpp_info.defines = ["APR_DECLARE_STATIC", ]
        else:
            libs = ["apr-1", ]
            if not self.options.shared:
                libs += ["pthread", ]
            self.cpp_info.includedirs = [os.path.join("include", "apr-1"), ]
        self.cpp_info.libs = libs
