#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools

import os

class ConanJson4ModernCppConan(ConanFile):
    name = "json4moderncpp"
    version = "3.7.3"
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    description = "A JSON library for Modern C++"
    license = "MIT License, Copyright © 2013-2019 Niels Lohmann"
    exports = ["LICENSE.md"]
    exports_sources = []
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/nlohmann/json"
    topics = ("conan", "json", "c++", "nlohmann")
    settings = "os", "arch", "compiler", "build_type"

    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = "json" + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["JSON_BuildTests"] = False
        cmake.definitions["JSON_MultipleHeaders"] = False
        cmake.configure(source_folder=self.source_subfolder)
        cmake.install()

    def package(self):
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
