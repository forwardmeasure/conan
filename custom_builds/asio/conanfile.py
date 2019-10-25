#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import tools
from conans.errors import ConanInvalidConfiguration

from forwardmeasure.conan_utils import ConfigurableConanFile


class AsioConan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/chriskohlhoff/asio"
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Asio is a cross-platform C++ library for network and low-level I/O"
    license = "BSL-1.0"
    topics = ("conan", "asio", "network", "io", "low-level")
    options = {
        "standalone": [True, False],
        "with_boost_regex": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "standalone": True,
        "with_boost_regex": False,
        "with_openssl": False,
    }
    settings = "os"
    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.options.standalone and self.options.with_boost_regex:
            raise ConanInvalidConfiguration(
                "'standalone' and 'with_boost_regex' are mutually exclusive! "
                "Please disable one of them."
            )

    def requirements(self):
        if self.options.with_boost_regex:
            self.requires.add(self.dependencies["boost"])

        if self.options.with_openssl:
            self.requires.add(self.dependencies["openssl"])

    def source(self):
        archive_name = "asio-" + self.version.replace(".", "-")
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, archive_name))
        extracted_name = "asio-" + archive_name
        os.rename(extracted_name, self._source_subfolder)

    def package(self):
        root_dir = os.path.join(self._source_subfolder, self.name)
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=root_dir)
        self.copy(pattern="*.hpp", dst="include", src=include_dir)
        self.copy(pattern="*.ipp", dst="include", src=include_dir)

    def package_info(self):
        if self.options.standalone:
            self.cpp_info.defines.append("ASIO_STANDALONE")
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

    def package_id(self):
        self.info.header_only()
