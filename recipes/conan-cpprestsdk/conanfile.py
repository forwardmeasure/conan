#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from conans import ConanFile, CMake, tools
from os import path, getcwd, environ, rename
import subprocess

def call(command):
    return subprocess.check_output(command, shell=False).strip()

def find_sysroot(sdk):
    return call(["xcrun", "--show-sdk-path", "-sdk", sdk])

class CppRestSDKConan(ConanFile):
    name = "cpprestsdk"
    version = "2.10.14"
    description = "A project for cloud-based client-server communication in native code using a modern asynchronous " \
                  "C++ API design"
    topics = ("conan", "cpprestsdk", "rest", "client", "http")
    url = "https://github.com/bincrafters/conan-cpprestsdk"
    homepage = "https://github.com/Microsoft/cpprestsdk"
    author = "Prashanth Nandavanam<pn@forwardmeasure.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "exclude_websockets": [True, False],
        "exclude_compression": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "exclude_websockets": False,
        "fPIC": True,
        "exclude_compression": False
    }

    zlib_reference = "zlib/1.2.11@forwardmeasure/stable"
    boost_reference = "boost/1.69.0@forwardmeasure/stable"
    asio_reference = "asio/1.13.0@forwardmeasure/stable"
    openssl_reference = "OpenSSL/1.1.1d@forwardmeasure/stable"
    websocketpp_reference = "websocketpp/0.8.1@forwardmeasure/stable"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    root = "%s-%s" % (name, version)
    short_paths = True

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def requirements(self):
        self.requires.add(self.openssl_reference)
        if not self.options.exclude_compression:
            self.requires.add(self.zlib_reference)
        if not self.options.exclude_websockets:
            self.requires.add(self.websocketpp_reference)
        self.requires.add(self.boost_reference)

    def source(self):
        sha256 = "f2628b248f714d7bbd6a536553bc3782602c68ca1b129017985dd70cc3515278"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version

        rename(extracted_dir, self._source_subfolder)

        if self.settings.compiler == 'clang' and str(self.settings.compiler.libcxx) in ['libstdc++', 'libstdc++11']:
            tools.replace_in_file(path.join(self._source_subfolder, 'Release', 'CMakeLists.txt'),
                                  'libc++', 'libstdc++')
        if self.settings.os == 'Android':
            tools.replace_in_file(path.join(self._source_subfolder, 'Release', 'cmake', 'cpprest_find_boost.cmake'), 'find_host_package', 'find_package')
            tools.replace_in_file(path.join(self._source_subfolder, 'Release', 'src', 'pch', 'stdafx.h'), '#include "boost/config/stdlib/libstdcpp3.hpp"', '//#include "boost/config/stdlib/libstdcpp3.hpp"')
            # https://github.com/Microsoft/cpprestsdk/issues/372#issuecomment-386798723
            tools.replace_in_file(path.join(self._source_subfolder, 'Release', 'src', 'http', 'client', 'http_client_asio.cpp'),
                                  'm_timer.expires_from_now(m_duration)',
                                  'm_timer.expires_from_now(std::chrono::microseconds(m_duration.count()))')

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                self._build_cmake()
        else:
            self._build_cmake()

    def _configure_cmake(self):
        if self.settings.os == "iOS":
            with open('toolchain.cmake', 'w') as toolchain_cmake:
                if self.settings.arch == "armv8":
                    arch = "arm64"
                    sdk = "iphoneos"
                elif self.settings.arch == "x86_64":
                    arch = "x86_64"
                    sdk = "iphonesimulator"
                sysroot = find_sysroot(sdk)
                toolchain_cmake.write('set(CMAKE_C_COMPILER /usr/bin/clang CACHE STRING "" FORCE)\n')
                toolchain_cmake.write('set(CMAKE_CXX_COMPILER /usr/bin/clang++ CACHE STRING "" FORCE)\n')
                toolchain_cmake.write('set(CMAKE_C_COMPILER_WORKS YES)\n')
                toolchain_cmake.write('set(CMAKE_CXX_COMPILER_WORKS YES)\n')
                toolchain_cmake.write('set(CMAKE_XCODE_EFFECTIVE_PLATFORMS "-%s" CACHE STRING "" FORCE)\n' % sdk)
                toolchain_cmake.write('set(CMAKE_OSX_ARCHITECTURES "%s" CACHE STRING "" FORCE)\n' % arch)
                toolchain_cmake.write('set(CMAKE_OSX_SYSROOT "%s" CACHE STRING "" FORCE)\n' % sysroot)
            environ['CONAN_CMAKE_TOOLCHAIN_FILE'] = path.join(getcwd(), 'toolchain.cmake')

        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_SAMPLES"] = False
        cmake.definitions["WERROR"] = False
        cmake.definitions["CPPREST_EXCLUDE_WEBSOCKETS"] = self.options.exclude_websockets
        cmake.definitions["CPPREST_EXCLUDE_COMPRESSION"] = self.options.exclude_compression
        cmake.definitions["CPPREST_VERSION"] = self.version
        cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info['OpenSSL'].rootpath
        cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = not self.options['OpenSSL'].shared
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["OPENSSL_MSVC_STATIC_RT"] = 'MT' in str(self.settings.compiler.runtime)
        if self.settings.os == "iOS":
            cmake.definitions["IOS"] = True
        elif self.settings.os == "Android":
            cmake.definitions["ANDROID"] = True
            cmake.definitions["CONAN_LIBCXX"] = ''
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("license.txt", dst="license", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=path.join(self._source_subfolder, "Release", "include"))
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            debug_suffix = 'd' if self.settings.build_type == 'Debug' else ''
            toolset = {'12': '120',
                       '14': '140',
                       '15': '141'}.get(str(self.settings.compiler.version))
            version_tokens = self.version.split(".")
            versioned_name = "cpprest%s_%s_%s%s" % (toolset, version_tokens[0], version_tokens[1], debug_suffix)
            # CppRestSDK uses different library name depends on CMAKE_VS_PLATFORM_TOOLSET
            if not path.isfile(path.join(self.package_folder, 'lib', '%s.lib' % versioned_name)):
                versioned_name = "cpprest_%s_%s%s" % (version_tokens[0], version_tokens[1], debug_suffix)
            lib_name = versioned_name
        else:
            lib_name = 'cpprest'
        self.cpp_info.libs.append(lib_name)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(["winhttp", "httpapi", "bcrypt"])
        if not self.options.shared:
            self.cpp_info.defines.append("_NO_ASYNCRTIMP")
