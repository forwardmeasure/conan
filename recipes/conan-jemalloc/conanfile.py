#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, stat, glob
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version


class JemallocConan(ConanFile):
    name = "jemalloc"
    version = "5.2.1"
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/jemalloc/jemalloc"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "A general purpose malloc(3) implementation that emphasizes fragmentation avoidance and scalable concurrency support"
    topics = "jemalloc", "malloc", "memory", "concurrency", "fragmentation", "speed"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "without-export": [True, False],
        "with-private-namespace": [True, False],
        "with-malloc-conf": [True, False],
        "enable-debug": [True, False],
        "disable-stats": [True, False],
        "enable-prof": [True, False],
        "enable-prof-libunwind": [True, False],
        "disable-prof-libgcc": [True, False],
        "disable-prof-gcc": [True, False],
        "disable-fill": [True, False],
        "disable-zone-allocator": [True, False],
        "enable-lazy-lock": [True, False],
        "disable-cache-oblivious": [True, False],
        "disable-syscall": [True, False],
        "disable-cxx": [True, False],
        "with-lg-page": [True, False],
        "with-lg-hugepage": [True, False],
        "with-lg-quantum": [True, False],
        "with-lg-vaddr": [True, False],
        "disable-initial-exec-tls": [True, False],
        "disable-libdl": [True, False],
    }
    default_options = {
        "shared": True,
        "without-export": False,
        "with-private-namespace": False,
        "with-malloc-conf": False,
        "enable-debug": False,
        "disable-stats": False,
        "enable-prof": False,
        "enable-prof-libunwind": False,
        "disable-prof-libgcc": False,
        "disable-prof-gcc": False,
        "disable-fill": False,
        "disable-zone-allocator": False,
        "enable-lazy-lock": False,
        "disable-cache-oblivious": False,
        "disable-syscall": False,
        "disable-cxx": False,
        "with-lg-page": False,
        "with-lg-hugepage": False,
        "with-lg-quantum": False,
        "with-lg-vaddr": False,
        "disable-initial-exec-tls": False,
        "disable-libdl": False,
    }

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.zip".format(self.homepage, self.version))
        extracted_dir = "jemalloc-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if (
            self.settings.os == "Windows"
            and self.settings.compiler == "Visual Studio"
            and Version(self.settings.compiler.version.value) < "14"
        ):
            raise ConanInvalidConfiguration("Abseil does not support MSVC < 14")

    def build(self):
        with tools.chdir(self._source_subfolder):
            for file in glob.glob("**/*.sh", recursive=True):
                os.chmod(file, stat.S_IRWXU)

            args = [""]
            for key, value in self.options.items():
                if key != "shared":
                    if value is True:
                        args += [
                            "--{}".format(key),
                        ]

            self.run("./autogen.sh {}".format(" ".join(args)))
            autotools = AutoToolsBuildEnvironment(self)
            env_build_vars = autotools.vars
            autotools.configure(vars=env_build_vars)
            autotools.make(vars=env_build_vars)
            autotools.install(vars=env_build_vars)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*.inc", dst="include", src=self._source_subfolder)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.lib", dst="lib", src=".", keep_path=False)
        self.copy("*.so", dst="lib", src=".", keep_path=False)
        self.copy("*.dll", dst="bin", src=".", keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["-Wl,--start-group"]

        self.cpp_info.libs.extend(tools.collect_libs(self))

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["-Wl,--end-group", "pthread"])
