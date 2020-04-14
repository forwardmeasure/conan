#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version


class AbseilConan(ConanFile):
    name = "abseil"
    version = "20190808"
    url = "https://github.com/bincrafters/conan-abseil"
    homepage = "https://github.com/abseil/abseil-cpp"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Abseil Common Libraries (C++) from Google"
    topics = "abseil", "algorithm", "container", "debugging", "hash", "memory", "meta", "numeric", "string", \
             "synchronization", "time", "types", "utility"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    requires = "cctz/2.3@bincrafters/stable"
    options = {"cxx_standard": [11, 14, 17], "build_testing": [True, False], "fPIC" : [True, False]}
    default_options = {"cxx_standard": 17, "build_testing": False, "fPIC": True}
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.zip".format(self.homepage, self.version))
        extracted_dir = "abseil-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version.value) < "14":
            raise ConanInvalidConfiguration("Abseil does not support MSVC < 14")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.definitions["BUILD_TESTING"] = self.options.build_testing
        cmake.definitions["CMAKE_CXX_STANDARD"] = self.options.cxx_standard
        cmake.definitions["ABSL_CCTZ_TARGET"] = "CONAN_PKG::cctz"
        cmake.configure()
        cmake.build()

    def _rename_libs(self):
        lib_dir = os.path.abspath("lib")
        for lib_name in os.listdir(lib_dir):
            new_lib_name = lib_name.replace("libabsl_absl", "libabsl")
            print ("Renaming %s to %s" % (lib_name, new_lib_name))
            os.rename(os.path.abspath(os.path.join(lib_dir, lib_name)), os.path.abspath(os.path.join(lib_dir, new_lib_name)))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*.inc", dst="include", src=self._source_subfolder)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.lib", dst="lib", src=".", keep_path=False)
        self.copy("*.so", dst="lib", src=".", keep_path=False)
        self.copy("*.dll", dst="bin", src=".", keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["-Wl,--start-group"]

        self.cpp_info.libs.extend(tools.collect_libs(self))

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["-Wl,--end-group", "pthread"])
        self._rename_libs()
