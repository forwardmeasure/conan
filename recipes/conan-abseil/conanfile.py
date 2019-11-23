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
    default_options = {"cxx_standard": 11, "build_testing": False, "fPIC": True}
    short_paths = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.zip".format(self.homepage, self.version))
        extracted_dir = "abseil-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and \
           self.settings.compiler == "Visual Studio" and \
           Version(self.settings.compiler.version.value) < "14":
            raise ConanInvalidConfiguration("Abseil does not support MSVC < 14")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.definitions["BUILD_TESTING"] = self.options.build_testing
        cmake.definitions["CMAKE_CXX_STANDARD"] = self.options.cxx_standard
        cmake.definitions["ABSL_CCTZ_TARGET"] = "CONAN_PKG::cctz"
        cmake.configure()
        cmake.build()

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
        self.cpp_info.libs.extend(["absl_dynamic_annotations",
                                   "absl_internal_spinlock_wait",
                                   "absl_bad_optional_access",
                                   "absl_leak_check",
                                   "absl_leak_check_disable",
                                   "absl_container",
                                   "absl_internal_city",
                                   "pow10_helper",
                                   "absl_bad_any_cast",
                                   "absl_int128",
                                   "absl_numeric",
                                   "absl_base",
                                   "absl_internal_throw_delegate",
                                   "absl_utility",
                                   "absl_meta",
                                   "absl_internal_malloc_internal",
                                   "absl_optional",
                                   "absl_span",
                                   "absl_demangle_internal",
                                   "absl_internal_debugging_internal",
                                   "absl_variant",
                                   "absl_any",
                                   "absl_strings",
                                   "absl_stacktrace",
                                   "absl_symbolize",
                                   "absl_hash",
                                   "str_format_extension_internal",
                                   "absl_raw_hash_set",
                                   "absl_internal_examine_stack",
                                   "str_format_internal",
                                   "absl_failure_signal_handler",
                                   "absl_str_format",
                                   "absl_time",
                                   "absl_synchronization"])
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
