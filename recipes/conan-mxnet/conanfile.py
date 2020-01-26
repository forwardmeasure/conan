from conans import ConanFile, CMake, tools, RunEnvironment
import os


class MxnetConan(ConanFile):
    name = "mxnet"
    version = "1.5.1"
    license = "Apache 2.0"
    homepage = "https://github.com/apache/incubator-mxnet"
    url = "https://github.com/forwardmeasure/conan"
    description = "Conan package for the MXNet machine learning library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "use_cuda": [True, False],
        "use_opencv": [True, False],
        "use_cudnn": [True, False],
        "use_openmp": [True, False],
        "use_mkldnn": [True, False],
        "use_lapack": [True, False],
        "use_operator_tuning": [True, False],
        "use_gperftools": [True, False],
        "use_jemalloc": [True, False],
    }

    default_options = (
        "shared=True",
        "use_cuda=False",
        "use_opencv=True",
        "use_cudnn=False",
        "use_openmp=True",
        "use_mkldnn=True",
        "use_lapack=False",
        "use_operator_tuning=False",
        "use_gperftools=False",
        "use_jemalloc=False",
    )
    generators = ("cmake", "virtualbuildenv", "virtualrunenv")
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("openblas/0.3.7@forwardmeasure/stable")

        if self.options.use_openmp:
            self.options["openblas"].USE_OPENMP = True

        self.options["openblas"].shared = self.options.shared

        if self.options.use_jemalloc:
            self.requires("jemalloc/5.2.1@forwardmeasure/stable")
            self.options["jemalloc"].shared = self.options.shared

        if self.options.use_lapack:
            self.requires("lapack/3.7.1@forwardmeasure/stable")
            self.options["lapack"].shared = self.options.shared
            self.options["openblas"].BUILD_WITHOUT_LAPACK = True

        if self.options.use_opencv:
            self.requires("opencv/4.2.0@forwardmeasure/stable")
            self.options["opencv"].shared = self.options.shared

    def source(self):
        # I'm sure there are better/more idiomatic ways to do this, but this will do for now
        git_clone_command = (
            "git clone {}.git {} && cd {} && " "git checkout {} && git submodule update --init --recursive"
        ).format(self.homepage, self._source_subfolder, self._source_subfolder, self.version)
        self.run(git_clone_command)

    def _configure_cmake(self):
        deps = "CONAN_PKG::openblas"
        if self.options.use_opencv:
            deps += " CONAN_PKG::opencv"
        if self.options.use_lapack:
            deps += " CONAN_PKG::lapack"
        if self.options.use_jemalloc:
            deps += " CONAN_PKG::jemalloc"

        tools.replace_in_file(
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/Utils.cmake)",
            """
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/Utils.cmake)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)
""",
        )

        tools.replace_in_file(
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "target_link_libraries(mxnet PRIVATE ${BEGIN_WHOLE_ARCHIVE} $<TARGET_FILE:mxnet_static> ${END_WHOLE_ARCHIVE})",
            "target_link_libraries(mxnet PRIVATE ${BEGIN_WHOLE_ARCHIVE} $<TARGET_FILE:mxnet_static> "
            + deps
            + " ${END_WHOLE_ARCHIVE})",
        )

        tools.replace_in_file(
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "list(APPEND mxnet_LINKER_LIBS lapack)",
            'message("USE_LAPACK ON-NON MSVC")',
        )

        cmake = CMake(self)
        cmake.definitions["USE_OLDCMAKECUDA"] = "OFF"
        cmake.definitions["USE_MKL_IF_AVAILABLE"] = "OFF"  # leave this off until intel does a better license
        cmake.definitions["USE_MKL_EXPERIMENTAL"] = "OFF"  # "
        cmake.definitions["USE_MKLML_MKL"] = "OFF"  # "
        cmake.definitions["USE_PROFILER"] = "OFF"
        cmake.definitions["USE_DIST_KVSTORE"] = "OFF"
        cmake.definitions["USE_PLUGINS_WARPCTC"] = "OFF"
        cmake.definitions["USE_CPP_PACKAGE"] = "ON"
        cmake.definitions["BUILD_CPP_EXAMPLES"] = "OFF"
        cmake.definitions["DO_NOT_BUILD_EXAMPLES"] = "ON"

        cmake.definitions["USE_CUDA"] = "ON" if self.options.use_cuda else "OFF"
        cmake.definitions["USE_CUDNN"] = "ON" if self.options.use_cudnn else "OFF"
        cmake.definitions["USE_OPENCV"] = "ON" if self.options.use_opencv else "OFF"
        cmake.definitions["USE_OPENMP"] = "ON" if self.options.use_openmp else "OFF"
        cmake.definitions["USE_LAPACK"] = "ON" if self.options.use_lapack else "OFF"
        cmake.definitions["USE_OPERATOR_TUNING"] = "ON" if self.options.use_operator_tuning else "OFF"
        cmake.definitions["USE_GPERFTOOLS"] = "ON" if self.options.use_gperftools else "OFF"
        cmake.definitions["USE_JEMALLOC"] = "ON" if self.options.use_jemalloc else "OFF"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))

        return cmake

    def build(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                self._build_cmake()
        else:
            self._build_cmake()

    def _build_cmake(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = self._configure_cmake()
            if self.options.shared:
                cmake.build(target="mxnet")
            else:
                cmake.build(target="mxnet_static")

            cmake.build(target="cpp_package_op_h")

    def package(self):
        if self.settings.compiler == "Visual Studio":
            cmake = CMake(self)
            cmake.install()
        else:
            self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

            # cpp package
            self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "cpp-package", "include"))
            self.copy(
                pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "cpp-package", "include")
            )

            # nnvm
            self.copy(
                pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "3rdparty", "nnvm", "include")
            )
            self.copy(
                pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "3rdparty", "nnvm", "include")
            )

            # dmlc
            self.copy(
                pattern="*.h",
                dst="include",
                src=os.path.join(self._source_subfolder, "3rdparty", "dmlc-core", "include"),
            )
            self.copy(
                pattern="*.hpp",
                dst="include",
                src=os.path.join(self._source_subfolder, "3rdparty", "dmlc-core", "include"),
            )

            if self.options.shared:
                self.copy(pattern="*.dylib", dst="lib", src="lib")
                self.copy(pattern="*.so", dst="lib", src="lib")

                self.copy(pattern="*.dylib", dst="lib", src=os.path.join(self._source_subfolder, "mxnet", "lib"))
                self.copy(pattern="*.so", dst="lib", src=os.path.join(self._source_subfolder, "mxnet", "lib"))

                self.copy(
                    pattern="*.dylib",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "nnvm", "lib"),
                )
                self.copy(
                    pattern="*.so",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "nnvm", "lib"),
                )

                self.copy(
                    pattern="*.dylib",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "dmlc-core", "lib"),
                )
                self.copy(
                    pattern="*.so",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "dmlc-core", "lib"),
                )

            else:
                self.copy(pattern="*.a", dst="lib", src="lib")
                self.copy(pattern="*.a", dst="lib", src=os.path.join(self._source_subfolder, "mxnet", "lib"))
                self.copy(
                    pattern="*.a",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "nnvm", "lib"),
                )
                self.copy(
                    pattern="*.a",
                    dst="lib",
                    src=os.path.join(self._source_subfolder, "mxnet", "3rdparty", "dmlc-core", "lib"),
                )

    def package_info(self):
        self.cpp_info.libs = ["mxnet", "dmlc"]
        if self.settings.compiler != "Visual Studio":
            self.cpp_info.libs.append("rt")
        if not self.options.shared:
            self.cpp_info.libs.extend(["nnvm"])
            if self.settings.os == "Macos":
                self.cpp_info.libs.insert(0, "-Wl,-all_load")
                self.cpp_info.libs.append("-Wl,-noall_load")
            elif self.settings.os != "Windows":
                self.cpp_info.libs.insert(0, "-Wl,--whole-archive")
                self.cpp_info.libs.append("-Wl,--no-whole-archive")

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
