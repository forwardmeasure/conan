from conans import ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class ONNXConan(ConanFile):
    name = "ONNX"
    version = "1.6.0"
    url = "https://github.com/forwardmeasure/conan"
    homepage = "https://github.com/onnx/onnx"
    topics = ("conan", "ONNX", "neural networks")
    author = "Prashanth Nandavanam <pn@forwardmeasure.com>"
    description = "ONNX - An open Neural Network Exchange"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = [
        "CMakeLists.txt",
        "FindONNX.cmake",
        "SelectLibraryConfigurations.cmake",
        "FindPackageMessage.cmake",
        "FindPackageHandleStandardArgs.cmake",
    ]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    short_paths = True  # Otherwise some folders go out of the 260 chars path length scope rapidly (on windows)

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_python": [True, False],
        "build_benchmarks": [True, False],
        "use_lite_proto": [True, False],
        "ifi_dummy_backend": [True, False],
        "build_tests": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "build_python": False,
        "build_benchmarks": False,
        "use_lite_proto": False,
        "ifi_dummy_backend": False,
        "build_tests": False,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = ("protobuf/3.12.1@forwardmeasure/stable",)

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = int(str(self.settings.compiler.version))
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name.lower() + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build_requirements(self):
        if self.options.build_tests:
            self.build_requires("benchmark/1.4.1@forwardmeasure/stable")
            self.build_requires("gflags/2.2.1@forwardmeasure/stable")

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.verbose = True

        cmake.definitions["BUILD_ONNX_PYTHON"] = "ON" if self.options.build_python else "OFF"
        cmake.definitions["ONNX_BUILD_BENCHMARKS"] = "ON" if self.options.build_benchmarks else "OFF"
        cmake.definitions["ONNX_USE_LITE_PROTO"] = "ON" if self.options.use_lite_proto else "OFF"
        cmake.definitions["ONNXIFI_DUMMY_BACKEND"] = "ON" if self.options.ifi_dummy_backend else "OFF"
        cmake.definitions["ONNX_BUILD_TESTS"] = "ON" if self.options.build_tests else "OFF"

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        cmake.definitions["ONNX_INSTALL"] = "ON"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                self._build_cmake()
        else:
            self._build_cmake()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.pdb", dst="lib", src=self._build_subfolder, keep_path=False)

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = [
            "onnx",
        ]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs += ["wsock32", "ws2_32"]
