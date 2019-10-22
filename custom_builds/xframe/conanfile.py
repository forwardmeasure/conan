#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os

from forwardmeasure.conan_utils import ConfigurableConanFile

class XframeConan(ConfigurableConanFile):
    (name, version, dependencies, exports) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/xtensor-stack/xframe"
    topics = ("conan", "quantstack", "tensor", "xframe", "container", "algorithm")
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "C++ Multi-dimensional labeled arrays and data frame based on xtensor"
    license = 'BSD 3-Clause "New" or "Revised" License'
    settings = "os", "arch", "compiler", "build_type"

    requires = dependencies["xtl"]

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
