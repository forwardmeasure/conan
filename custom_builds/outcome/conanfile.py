#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import tools

from forwardmeasure.conan_utils import ConfigurableConanFile

class OutcomeConan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    url = "https://github.com/forwardmeasure/conan-outcome"
    author = "Prashanth Nandavanam <pn@forwardmeasure.com>"
    description = "A C++14 library for reporting and handling function failures that can be used as a substitute for, or a complement to, the exception handling mechanism."
    license = "Apache-2.0"
    source_subfolder = "source_subfolder"

    def source(self):
        source_url = "https://github.com/ned14/outcome"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version), verify=False)
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_folder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

    def package(self):
        include_folder = os.path.join(self.source_subfolder, "single-header")
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
