#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools

class OutcomeConan(ConanFile):
    name = "outcome"
    version = "master"
    author = "Prashanth Nandavanam <pn@forwardmeasure.com>"
    description = "A C++14 library for reporting and handling function failures that can be used as a substitute for, or a complement to, the exception handling mechanism."
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = []
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/ned14/outcome"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version), verify=False)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def package(self):
        include_folder = os.path.join(self.source_subfolder, "single-header")
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
