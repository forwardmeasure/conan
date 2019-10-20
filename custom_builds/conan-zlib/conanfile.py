#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from conans import ConanFile, CMake, tools, RunEnvironment
from conans.tools import download, unzip
from conans.errors import ConanInvalidConfiguration

from forwardmeasure.utils import ConfigUtils


class ZlibConan(ConanFile):
    """A  Conan recipe for installing Google protocol Buffers
       Adapted from https://github.com/conan-io/conan-center-index"""

    CFG_FILE_NAME = "config.ini"
    my_config = ConfigUtils().read_config(CFG_FILE_NAME)

    name = my_config["PACKAGE"]["name"]
    version = my_config["PACKAGE"]["version"]
    dependencies = my_config["DEPENDENCIES"]
    ZIP_FOLDER_NAME = "zlib-%s" % version

    url = "https://github.com/forwardmeasure/conan"
    homepage = ""
    topics = ""
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    license = "http://www.zlib.net/zlib_license.html"
    exports = ["LICENSE.md", "config.ini"]
    exports_sources = ["CMakeLists.txt", "FindZLIB.cmake"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tests": [True, False]
    }
    default_options = {"shared": True, "fPIC": True, "build_tests": False}

    def config(self):
        del self.settings.compiler.libcxx

    def source(self):
        zip_name = "zlib-%s.tar.gz" % self.version
        download(
            "http://downloads.sourceforge.net/project/libpng/zlib/%s/%s" %
            (self.version, zip_name), zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        os.rename(self.ZIP_FOLDER_NAME, "sources")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        # Copy findZLIB.cmake to package
        self.copy("FindZLIB.cmake", ".", ".")

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                    self.cpp_info.libs = ['zlibd']
                else:
                    self.cpp_info.libs = ['zlib']
            else:
                if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                    self.cpp_info.libs = ['zlibstaticd']
                else:
                    self.cpp_info.libs = ['zlibstatic']
        else:
            self.cpp_info.libs = ['z']
