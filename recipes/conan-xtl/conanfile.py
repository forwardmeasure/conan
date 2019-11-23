#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os

class ConanXtlConan(ConanFile):
    name = "xtl"
    version = "0.6.8"
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Basic tools (containers, algorithms) used by other quantstack packages"
    license = 'BSD 3-Clause "New" or "Revised" License'                  
    exports = ["LICENSE.md"]
    exports_sources = []
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/xtensor-stack/xtl"
    topics = ("conan", "quantstack", "tensor", "xframe", "container", "algorithm")
    settings = "os", "arch", "compiler", "build_type"

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
