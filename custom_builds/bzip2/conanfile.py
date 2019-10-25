#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import CMake, tools

from forwardmeasure.conan_utils import ConfigurableConanFile


class Bzip2Conan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    url = "https://github.com/enthought/bzip2-1.0.6"
    homepage = "http://www.bzip.org"
    author = "Conan Community"
    license = "bzip2-1.0.6"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows–Wheeler algorithm."
    topics = ("conan", "bzip2", "data-compressor", "file-compression")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False],
    }
    default_options = "shared=True", "fPIC=True", "build_executable=True"
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        _version = "master"
        folder_name = "%s-%s-%s" % (self.name, self.version, _version)
        zip_name = "%s.tar.gz" % folder_name
        sha256 = "eba642d8233b45c1c50d928d2ca7b98e7fcb294dae3e1c7d6f4cdf82f2f3994e"
        #       tools.get(url="%s/download_file?file_path=%s" % (url, zip_name), sha256=sha256, filename=zip_name)
        tools.get(
            "{0}/archive/{1}.tar.gz".format(self.url, _version),
            sha256=sha256,
            filename=zip_name,
        )

        os.rename(folder_name, self._source_subfolder)

    def _configure_cmake(self):
        major = self.version.split(".")[0]
        cmake = CMake(self)
        cmake.definitions["BZ2_VERSION_STRING"] = self.version
        cmake.definitions["BZ2_VERSION_MAJOR"] = major
        cmake.definitions["BZ2_BUILD_EXE"] = (
            "ON" if self.options.build_executable else "OFF"
        )
        cmake.configure()
        return cmake

    def build(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "bzip2.c"),
            r"<sys\stat.h>",
            "<sys/stat.h>",
        )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bz2"]
