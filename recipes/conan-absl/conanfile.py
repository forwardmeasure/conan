#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools

import os


class ConanAbseil(ConanFile):
    name = "absl"
    version = "20200225.2"
    url = "https://github.com/bincrafters/conan-abseil"
    homepage = "https://github.com/abseil/abseil-cpp"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Abseil Common Libraries (C++) from Google"
    topics = (
        "abseil",
        "algorithm",
        "container",
        "debugging",
        "hash",
        "memory",
        "meta",
        "numeric",
        "string",
        "synchronization",
        "time",
        "types",
        "utility",
    )
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    requires = "cctz/2.3@bincrafters/stable"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx_standard": [11, 14, 17],
        "build_testing": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "cxx_standard": 14,
        "build_testing": False,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.zip".format(self.homepage, self.version))
        extracted_dir = "abseil-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_TESTING"] = self.options.build_testing
        cmake.definitions["CMAKE_CXX_STANDARD"] = self.options.cxx_standard
        cmake.definitions["ABSL_CCTZ_TARGET"] = "CONAN_PKG::cctz"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="license", src=self._source_subfolder)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["-Wl,--start-group"]

        self.cpp_info.libs.extend(tools.collect_libs(self))

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["-Wl,--end-group", "pthread"])
