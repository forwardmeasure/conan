#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version

from forwardmeasure.conan_utils import ConfigurableConanFile


class AbseilConan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/abseil/abseil-cpp"
    topics = ""
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Abseil Common Libraries (C++) from Google"
    license = "Apache 2.0"
    settings = "os", "arch", "compiler", "build_type"

    requires = dependencies["cctz"]

    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _commit_id = "fcb104594b0bb4b8ac306cb2f55ecdad40974683"

    def source(self):
        tools.get("{0}/archive/{1}.zip".format(self.homepage, self._commit_id))
        extracted_dir = "abseil-cpp-" + self._commit_id
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if (
            self.settings.os == "Windows"
            and self.settings.compiler == "Visual Studio"
            and Version(self.settings.compiler.version.value) < "14"
        ):
            raise ConanInvalidConfiguration("Abseil does not support MSVC < 14")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["ABSL_CCTZ_TARGET"] = "CONAN_PKG::cctz"
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*.inc", dst="include", src=self._source_subfolder)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.lib", dst="lib", src=".", keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["-Wl,--start-group"]

        self.cpp_info.libs.extend(tools.collect_libs(self))

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["-Wl,--end-group", "pthread"])
