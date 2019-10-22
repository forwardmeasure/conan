#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from conans import ConanFile, CMake, tools, RunEnvironment
from conans.tools import download, unzip
from conans.errors import ConanInvalidConfiguration

from forwardmeasure.conan_utils import ConfigurableConanFile


class ZlibConan(ConfigurableConanFile):
    """A  Conan recipe for installing Google protocol Buffers
       Adapted from https://github.com/conan-io/conan-center-index"""

    (name, version, dependencies, exports) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindZLIB.cmake"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/madler/zlib"
    topics = ""
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    license = "http://www.zlib.net/zlib_license.html"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tests": [True, False]
    }
    default_options = {"shared": True, "fPIC": True, "build_tests": False}

    generators = "cmake"
    source_subfolder = "source_subfolder"

    ZIP_FOLDER_NAME = "zlib-%s" % version

    def config(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("{0}/archive/v{1}.zip".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure()

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
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
