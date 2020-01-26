#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, tools


class ConanXtensorIoConan(ConanFile):
    name = "xtensor-io"
    version = "0.9.0"
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "Library for reading and writing image, sound and npz file formats to and from xtensor data structures."
    license = 'BSD 3-Clause "New" or "Revised" License'
    exports = ["LICENSE.md"]
    exports_sources = []
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/xtensor-stack/xtensor-io"
    topics = ("conan", "quantstack", "tensor", "xtensor-io", "hdf5", "npz")
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
