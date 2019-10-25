#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import AutoToolsBuildEnvironment, tools, MSBuild, CMake
from conans.errors import ConanException
from conans.tools import os_info, SystemPackageTool

from forwardmeasure.conan_utils import ConfigurableConanFile


class Apachelog4cxxConan(ConfigurableConanFile):
    (
        name,
        version,
        dependencies,
        exports,
    ) = ConfigurableConanFile.init_conan_config_params()
    exports += ["LICENSE.md"]
    exports_sources = "char_widening.patch"

    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/apache/logging-log4cxx"
    license = "Apache-2.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "enable-wchar_t" : ["yes", "no"],
        "enable-unichar" : ["yes", "no"],
        "enable-cfstring" : ["yes", "no"],
        "with-logchar" : ["utf-8", "wchar_t", "unichar"],
        "with-charset" : ["utf-8", "iso-8859-1", "usascii", "ebcdic", "auto"],
        "with-SMTP" : ["libesmtp", "no"],
        "with-ODBC" : ["unixODBC", "iODBC", "Microsoft", "no"]
    }
    default_options = "enable-wchar_t=yes", "enable-unichar=no", "enable-cfstring=no", "with-logchar=utf-8", "with-charset=auto", "with-SMTP=no", "with-ODBC=no", "shared=True"
    lib_name = "logging-log4cxx-" + version.replace('.', '_')
    generators = "cmake"

    def requirements(self):
        self.requires.add(self.dependencies["apache-apr"])
        self.requires.add(self.dependencies["apache-apr-util"])

    def source(self):
        tools.get("https://github.com/apache/logging-log4cxx/archive/{version}.tar.gz".format(version=self.version.replace(".", "_")))

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.definitions["APR_ALTLOCATION"] = self.deps_cpp_info["apache-apr"].rootpath
            cmake.definitions["APRUTIL_ALTLOCATION"] = self.deps_cpp_info["apache-apr-util"].rootpath
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            cmake.configure()
            cmake.build()
            cmake.install()
        else:
            with tools.chdir(self.lib_name):
                self.run("./autogen.sh")

            env_build = AutoToolsBuildEnvironment(self)
            args = ['--prefix', self.package_folder,
                    '--with-apr={}'.format(os.path.join(self.deps_cpp_info["apache-apr"].rootpath)),
                    '--with-apr-util={}'.format(os.path.join(self.deps_cpp_info["apache-apr-util"].rootpath)),
                    ]
            for key, value in self.options.items():
                if key != 'shared':
                    args += ["--{}={}".format(key, value), ]
                else:
                    args += ["--enable-{}={}".format(key, value), ]

            env_build.configure(configure_dir=self.lib_name, host=self.settings.arch, args=args)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy("*.so*", dst="lib", src="lib", keep_path=False)
        self.copy("*.dylib*", dst="lib", src="lib", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)
        self.copy("*.h", dst="include", src="include", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["log4cxx"]
