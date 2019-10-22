#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration

from forwardmeasure.conan_utils import ConfigurableConanFile


class ProtobufConan(ConfigurableConanFile):
    """A Conan recipe for installing Google protocol Buffers"""
    """ Adadpted from https://github.com/bincrafters/conan-protobuf"""

    (name, version, dependencies, exports) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = [
        "CMakeLists.txt", "FindProtobuf.cmake",
        "SelectLibraryConfigurations.cmake", "FindPackageMessage.cmake",
        "FindPackageHandleStandardArgs.cmake"
    ]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/protocolbuffers/protobuf"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler",
              "serialization", "rpc")
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Protocol Buffers - Google's data interchange format"
    license = "BSD-3-Clause"

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "shared": [True, False],
        "with_zlib": [True, False],
        "fPIC": [True, False],
        "lite": [True, False]
    }
    default_options = {
        "with_zlib": True,
        "shared": True,
        "fPIC": True,
        "lite": False
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = Version(self.settings.compiler.version.value)
            if compiler_version < "14":
                raise ConanInvalidConfiguration(
                    "On Windows, the protobuf/3.6.x package can only be built with the "
                    "Visual Studio 2015 or higher.")

    def requirements(self):
        if self.options.with_zlib:
            self.requires(self.dependencies["zlib"])

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage,
                                                   self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = True
        cmake.definitions["protobuf_BUILD_PROTOBUF_LITE"] = True
        if self.settings.compiler == "Visual Studio":
            cmake.definitions[
                "protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("FindProtobuf.cmake", ".", ".")
        self.copy("SelectLibraryConfigurations.cmake", ".", ".")
        self.copy("FindPackageMessage.cmake", ".", ".")
        self.copy("FindPackageHandleStandardArgs.cmake", ".", ".")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]
