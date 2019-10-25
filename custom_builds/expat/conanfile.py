#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import CMake, tools
from conans.errors import ConanException

from forwardmeasure.conan_utils import ConfigurableConanFile


class ExpatConan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    
    description = "Recipe for Expat library"
    license = "MIT/X Consortium license. Check file COPYING of the library"
    url = "https://github.com/forwardmeasure/conan-expat"
    source_url = "https://github.com/libexpat/libexpat"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "static_crt": [True, False],
               "disable_getrandom": [True, False],
              }
    default_options = "shared=True", \
        "disable_getrandom=True", \
        "static_crt=False"

    generators = "cmake"

    def source(self):
        self.run("git clone --depth 1 --branch R_2_2_6 %s" % self.source_url)

    def build(self):
        tools.replace_in_file("libexpat/expat/CMakeLists.txt", "cmake_minimum_required(VERSION 2.8.10)",
                              """cmake_minimum_required(VERSION 2.8.10)
                              include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
                              conan_basic_setup()
                              """)

        cmake = CMake(self)

        cmake_args = { "BUILD_doc" : "OFF",
                       "BUILD_examples" : "OFF",
                       "BUILD_shared" : self.options.shared,
                       "BUILD_tests" : "OFF",
                       "BUILD_tools" : "OFF",
                       "CMAKE_POSITION_INDEPENDENT_CODE": "ON",
                       "CMAKE_DEBUG_POSTFIX": "",
                       "MSVC_USE_STATIC_CRT": self.options.static_crt,
                     }

        cmake.configure(source_dir="../libexpat/expat", build_dir="build", defs=cmake_args)

        try:
            if self.options.disable_getrandom:
                tools.replace_in_file("build/expat_config.h", "#define HAVE_GETRANDOM",
                                                              "// #undef HAVE_GETRANDOM")
                self.output.success("HAVE_GETRANDOM has been undefined by user request")
        except ConanException:
            self.output.warn("HAVE_GETRANDOM could not be undefined. It was not defined")

        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["expat"]
        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]

    def configure(self):
        del self.settings.compiler.libcxx
