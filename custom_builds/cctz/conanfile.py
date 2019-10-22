#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

from forwardmeasure.conan_utils import ConfigurableConanFile


class CCTZConan(ConfigurableConanFile):
    (name, version, dependencies, exports) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/google/cctz"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ""
    description = "C++ library for translating between absolute and civil times"
    license = "Apache 2.0"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_tools": [True, False]
    }
    default_options = {"fPIC": True, "shared": True, "build_tools": False}
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and \
            self.settings.compiler == "Visual Studio" and \
            float(self.settings.compiler.version.value) < 14:
            raise ConanInvalidConfiguration("CCTZ requires MSVC >= 14")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage,
                                                   self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # this is a specific patch to the CMakeLists.txt which MUST be remove iff ( cctz version > 2.2 )
        _cmakelists_new = "https://raw.githubusercontent.com/google/cctz/8768b6d02283f6226527c1a7fb39c382ddfb4cec/CMakeLists.txt"
        _cmakelists_old = os.path.join(self._source_subfolder,
                                       "CMakeLists.txt")
        tools.download(_cmakelists_new,
                       _cmakelists_old,
                       overwrite=True,
                       verify=False)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TOOLS"] = self.options.build_tools
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure()
        cmake.build()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE.txt",
                  dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
