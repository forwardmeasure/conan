#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, tools

from forwardmeasure.conan_utils import ConfigurableConanFile


class ConanXtlConan(ConfigurableConanFile):
    """A Conan recipe for installing the XTL header-only library"""

    (name, version, dependencies, exports) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = []

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/xtensor-stack/xtl"
    topics = ("conan", "quantstack", "tensor", "xtl", "container", "algorithm")
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Basic tools (containers, algorithms) used by other quantstack packages"
    license = 'BSD 3-Clause "New" or "Revised" License'
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
