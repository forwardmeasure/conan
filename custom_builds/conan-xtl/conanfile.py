#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, tools

from forwardmeasure.utils import ConfigUtils


class ConanXtlConan(ConanFile):
    """A Conan recipe for installing the XTL header-only library"""

    CFG_FILE_NAME = "config.ini"
    my_config = ConfigUtils().read_config(CFG_FILE_NAME)

    name = my_config["PACKAGE"]["name"]
    version = my_config["PACKAGE"]["version"]
    dependencies = my_config["DEPENDENCIES"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/xtensor-stack/xtl"
    topics = ("conan", "quantstack", "tensor", "container", "algorithm")
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Basic tools (containers, algorithms) used by other quantstack packages"

    license = "BSD-3-Clause"
    exports = ["LICENSE.md", "config.ini"]
    exports_sources = []
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def package(self):
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
