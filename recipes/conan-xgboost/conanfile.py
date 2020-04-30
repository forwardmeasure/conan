from conans import ConanFile, CMake, tools, RunEnvironment
import os
import glob


class XGBoostConan(ConanFile):
    name = "xgboost"
    version = "1.0.2"
    description = (
        "A scalable, Portable and Distributed Gradient Boosting (GBDT, GBRT or GBM)"
        "Library, for Python, R, Java, Scala, C++ and more"
    )
    topics = {"XGBoost", "extreme gradient boosting", "GBDT", "GBRT", "GBM"}
    license = "BSD-3-Clause"
    homepage = "https://github.com/dmlc/xgboost"
    url = "https://github.com/forwardmeasure/conan"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "USE_OPENMP": [True, False],
        "JVM_BINDINGS": [True, False],
        "R_LIB": [True, False],
        "USE_CUDA": [True, False],
        "USE_NCCL": [True, False],
        "BUILD_WITH_SHARED_NCCL": [True, False],
        "USE_HDFS": [True, False],
        "USE_AZURE": [True, False],
        "USE_S3": [True, False],
        "PLUGIN_LZ4": [True, False],
        "PLUGIN_DENSE_PARSER": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "USE_OPENMP": False,
        "JVM_BINDINGS": False,
        "R_LIB": False,
        "USE_CUDA": False,
        "USE_NCCL": False,
        "BUILD_WITH_SHARED_NCCL": False,
        "USE_HDFS": False,
        "USE_AZURE": False,
        "USE_S3": False,
        "PLUGIN_LZ4": False,
        "PLUGIN_DENSE_PARSER": False,
    }
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires.add("zlib/1.2.11@conan/stable")

    ################################################################################################################
    #
    ################################################################################################################
    def source(self):
        # I'm sure there are better/more idiomatic ways to do this, but this will do for now
        git_clone_command = (
            "git clone {}.git {} && cd {} && " "git checkout v{} && git submodule update --init --recursive"
        ).format(self.homepage, self._source_subfolder, self._source_subfolder, self.version)
        self.run(git_clone_command)

    def source_new(self):
        tools.get("{0}/archive/v{1}.zip".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_cmake(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = self._configure_cmake()
            cmake.build()

    def _patch(self):
        if self.settings.os != "Windows":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "target_link_libraries(runxgboost PRIVATE ${LINKED_LIBRARIES_PRIVATE})",
                "target_link_libraries(runxgboost PRIVATE ${LINKED_LIBRARIES_PRIVATE} pthread)",
            )

    def build(self):
        self._patch()
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                self._build_cmake()
        else:
            self._build_cmake()

    def _configure_cmake(self):
        cmake = CMake(self, parallel=self.settings.os != "Windows")
        cmake.definitions["USE_OPENMP"] = "ON" if self.options.USE_OPENMP else "OFF"
        cmake.definitions["JVM_BINDINGS"] = "ON" if self.options.JVM_BINDINGS else "OFF"
        cmake.definitions["R_LIB"] = "ON" if self.options.R_LIB else "OFF"
        cmake.definitions["USE_CUDA"] = "ON" if self.options.USE_CUDA else "OFF"
        cmake.definitions["USE_NCCL"] = "ON" if self.options.USE_NCCL and self.options.USE_CUDA else "OFF"
        cmake.definitions["BUILD_WITH_SHARED_NCCL"] = (
            "ON" if self.options.BUILD_WITH_SHARED_NCCL and self.options.USE_CUDA else "OFF"
        )

        cmake.definitions["USE_HDFS"] = "ON" if self.options.USE_HDFS else "OFF"
        cmake.definitions["USE_AZURE"] = "ON" if self.options.USE_AZURE else "OFF"
        cmake.definitions["USE_S3"] = "ON" if self.options.USE_S3 else "OFF"
        cmake.definitions["PLUGIN_LZ4"] = "ON" if self.options.PLUGIN_LZ4 else "OFF"
        cmake.definitions["PLUGIN_DENSE_PARSER"] = "ON" if self.options.PLUGIN_DENSE_PARSER else "OFF"

        cmake.configure(
            source_folder=os.path.join(self.source_folder, self._source_subfolder), build_folder=self._build_subfolder
        )

        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["xgboost"]
        if self.options.USE_CUDA:
            self.cpp_info.libs.extend(["nvrtc", "cudart", "cuda"])

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "m", "dl"])

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]

