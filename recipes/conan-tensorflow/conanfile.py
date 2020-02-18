import os
import subprocess
import platform
import shutil
import sys
from pathlib import Path
import fnmatch
import functools
import itertools

from conans import ConanFile, tools


class TensorFlowConan(ConanFile):
    name = "tensorflow"
    version = "2.1.0"
    homepage = "https://github.com/tensorflow/tensorflow"
    topics = ("conan", "tensorflow", "Machine Learning", "Neural Networks")
    url = "https://github.com/forwardmeasuyre/conan"
    description = "A Conan recipe to build Tensorflow C++ from code"
    author = "Prashanth Nandavanam <pn@forwardmeasure.com>"
    license = "Apache-2.0"
    exports = ["LICENSE.md", "tensorflow.pc.in", "tensorflow.pc"]
    exports_sources = ["tensorflow.pc.in", "tensorflow.pc"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cuda_clang": [True, False],
        "download_clang": [True, False],
        "build_optimized": [True, False],
        "build_monolithic": [True, False],
        "set_android_workspace": [True, False],
        "build_dynamic_kernels": [True, False],
        "need_gcp": [True, False],
        "need_gdr": [True, False],
        "need_cuda": [True, False],
        "need_hdfs": [True, False],
        "need_opencl": [True, False],
        "need_jemalloc": [True, False],
        "enable_xla": [True, False],
        "need_verbs": [True, False],
        "download_mkl": [True, False],
        "need_mkl": [True, False],
        "need_ngraph": [True, False],
        "need_aws": [True, False],
        "need_mpi": [True, False],
        "need_s3": [True, False],
        "need_opencl_sycl": [True, False],
        "need_computecpp": [True, False],
        "need_kafka": [True, False],
        "need_tensorrt": [True, False],
        "need_ignite": [True, False],
        "need_rocm": [True, False],
        "need_numa": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "cuda_clang": False,
        "download_clang": False,
        "build_optimized": True,
        "build_monolithic": False,
        "build_dynamic_kernels": False,
        "need_gcp": False,
        "need_gdr": False,
        "need_cuda": False,
        "need_hdfs": False,
        "need_opencl": False,
        "need_jemalloc": False,
        "enable_xla": True,
        "need_verbs": False,
        "download_mkl": False,
        "need_mkl": True,
        "need_ngraph": False,
        "need_aws": False,
        "need_mpi": False,
        "need_s3": False,
        "need_opencl_sycl": False,
        "need_computecpp": False,
        "set_android_workspace": False,
        "need_kafka": False,
        "need_tensorrt": False,
        "need_ignite": False,
        "need_rocm": False,
        "need_numa": False,
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _bazel_cache_dir = os.path.join(os.environ["CONAN_USER_HOME"], "BAZEL_CACHE")
    _grpc_version = "1.26.0"
    _protobuf_version = "3.8.0"

    short_paths = True
    exports = ["patches/*"]

    ################################################################################################################
    #
    ################################################################################################################
    def build_requirements(self):
        if not tools.which("bazel"):
            self.build_requires("bazel_installer/1.1.0@bincrafters/stable")
        self.build_requires("OpenSSL/1.1.1d@forwardmeasure/stable")
        self.build_requires("grpc/1.26.0@forwardmeasure/stable")
        self.build_requires("protobuf/3.8.0@forwardmeasure/stable")

    ################################################################################################################
    #
    ################################################################################################################
    def _find_directory_under_directory(self, head_dir, dir_name):
        outputList = []
        for root, dirs, _ in os.walk(head_dir):
            for d in dirs:
                if d.upper() == dir_name.upper():
                    outputList.append(os.path.join(root, d))
        return outputList

    ################################################################################################################
    #
    ################################################################################################################
    def _build_bazel_target(self, bazel_config_flags, target, static_link_stdcpp):
        print(
            "_build_bazel_target(): installing target {} with {} link".format(
                target, "static" if static_link_stdcpp else "dynamic"
            )
        )
        env_build = dict()
        # This is a shite, ugly hack. Linking with devtoolset on Bazel is jacked.
        if static_link_stdcpp:
            #            env_build["BAZEL_LINKOPTS"] = "-static-libstdc++:-lm"
            env_build["BAZEL_LINKLIBS"] = "-l%:libstdc++.a"

        with tools.environment_append(env_build):
            build_cmd = (
                "bazel --output_user_root={} --host_jvm_args=-Xms512M --host_jvm_args=-Xmx8192M build -s --jobs 12"
                " --incompatible_no_support_tools_in_action_inputs=false --nodiscard_analysis_cache --keep_state_after_build"
                " --track_incremental_state --verbose_failures {} {}"
            ).format(self._bazel_cache_dir, bazel_config_flags, target)
            print("Running bazel command [{}]".format(build_cmd))
            self.run(build_cmd)

    ################################################################################################################
    #
    ################################################################################################################
    def _copy_file(self, src_file: str, dest_dir: str, verbose=True) -> str:
        print("_copy_file(): copying {} to {}".format(src_file, dest_dir))

        if src_file is None:
            print("_copy_file(): cannot process null source {}".format(src_file))
            return None

        if dest_dir is None:
            print("_copy_file(): cannot process null source {}".format(dest_dir))
            return None

        if not os.path.isfile(src_file) and not os.path.islink(src_file):
            print("_copy_file(): source {} must be a file or link".format(src_file))
            return None

        if not os.path.isdir(dest_dir):
            print("_copy_file(): destination must be a directory and not a file")
            return None

        if os.path.islink(src_file):
            # Step down one level of indirection
            linkto = os.readlink(src_file)
            print("_copy_file(): {} links to {}".format(src_file, linkto))

            if not os.path.isabs(linkto):
                linkto = os.path.join(os.path.split(src_file)[0], linkto)

            # Recurse and get the link target
            dest = self._copy_file(linkto, dest_dir, verbose)
            dest_link = os.path.join(dest_dir, os.path.basename(src_file))

            if dest != dest_link:
                subprocess.call("ln -sf {} {}".format(dest, dest_link), shell=True)
                print("_copy_file(): linked {} to {}".format(dest_link, dest))

            return dest_link
        else:
            dest_file = os.path.join(dest_dir, os.path.basename(src_file))
            print("_copy_file(): copying {} as {}".format(src_file, dest_file))

            copy_str = "cp -f {} {}".format(src_file, dest_file)
            print("_copy_file(): invoking shell [{}]".format(copy_str))
            subprocess.call(copy_str, shell=True)
            print("Returning {}".format(dest_file))

            return dest_file

    ################################################################################################################
    #
    ################################################################################################################
    def _find_file(self, src_dir: str, file_name: str) -> str:
        print("_find_file(): looking for file {} under {}".format(file_name, src_dir))
        for root, _, files in os.walk(src_dir):
            if file_name in files:
                found_file = os.path.join(root, file_name)
                print("_find_file(): found file, returning {}".format(found_file))
                return found_file
        return None

    ################################################################################################################
    #
    ################################################################################################################
    def _find_files(self, src_dir: str, search_patterns: [str] = None) -> [str]:
        """
        Returns a generator yielding files matching the given patterns
        :type src_dir: str
        :type search_patterns: [str]
        :rtype : [str]
        :param src_dir: Directory to search for files/directories under. Defaults to current dir.
        :param search_patterns: Patterns of files to search for. Defaults to ["*"]. Example: ["*.json", "*.xml"]
        """
        path = src_dir or "."
        path_patterns = search_patterns or ["*.so", "*.dylib"]

        for root_dir, _, file_names in os.walk(path):
            filter_partial = functools.partial(fnmatch.filter, file_names)

            for file_name in itertools.chain(*map(filter_partial, path_patterns)):
                yield os.path.join(root_dir, file_name)

    ################################################################################################################
    #
    ################################################################################################################
    def _copy_tf_libs(self, src_dir, dest_dir, search_patterns: [str] = None):
        try:
            if search_patterns is None:
                search_patterns = ["*.so", "*.dylib"]

            print(
                "_copy_tf_libs(): copying file matching patterns {} from {} to {}".format(
                    str(search_patterns), src_dir, dest_dir
                )
            )

            for f in self._find_files(src_dir=src_dir, search_patterns=search_patterns):
                print("Copying {} to {}".format(f, dest_dir))
                self._copy_file(f, dest_dir, verbose=True)

        except Exception as inst:
            print("Exception caught copying tf libs")
            print(inst)

    ################################################################################################################
    #
    ################################################################################################################
    def _fix_up_pkgconfig_file(self):
        self.copy(pattern="tensorflow.pc.in", dst="tensorflow.pc", src=self._source_subfolder)
        tools.replace_in_file("tensorflow.pc", "@version@", self.version, strict=True)
        tools.replace_in_file("tensorflow.pc", "@prefix@", self.package_folder, strict=True)

    ################################################################################################################
    #
    ################################################################################################################
    def _copy_tf_extra_headers(self, head_dir, dest_dir, rel_path, search_pattern="*.h"):
        for file in Path(head_dir).rglob(search_pattern):
            (head, tail) = os.path.split(file)

            rel_path_stub = os.path.relpath(head, rel_path)
            dest_dir_inner = os.path.join(dest_dir, rel_path_stub)

            if not os.path.exists(dest_dir_inner):
                os.makedirs(dest_dir_inner, exist_ok=True)

            dest_file = os.path.join(dest_dir_inner, tail)
            shutil.copyfile(file, dest_file)

    ################################################################################################################
    #
    ################################################################################################################
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    ################################################################################################################
    #
    ################################################################################################################
    def source(self):
        # I'm sure there are better/more idiomatic ways to do this, but this will do for now
        git_clone_command = (
            "git clone {}.git {} && cd {} && " "git checkout v{} && git submodule update --init --recursive"
        ).format(self.homepage, self._source_subfolder, self._source_subfolder, self.version)
        self.run(git_clone_command)

    ################################################################################################################
    #
    ################################################################################################################
    def _add_lib_to_env(self, dependency_name: str, tf_lib_name: str, env_build: dict):
        lib_root_path = self.deps_cpp_info[dependency_name].rootpath

        tf_syslibs_env_var = "TF_SYSTEM_LIBS"
        if tf_syslibs_env_var in env_build:
            env_build[tf_syslibs_env_var] += "," + format(tf_lib_name)
        else:
            env_build[tf_syslibs_env_var] = tf_lib_name

        env_build[tf_lib_name + "_PREFIX"] = lib_root_path
        env_build[tf_lib_name + "_LIBDIR"] = os.path.join(lib_root_path, "lib")
        env_build[tf_lib_name + "_INCLUDEDIR"] = os.path.join(lib_root_path, "include")

    ################################################################################################################
    # We need to patch a few files until they are merged into the TF baseline
    ################################################################################################################
    def _patch_tf_files(self):
        source_folder = os.path.join(self.build_folder, self._source_subfolder)

        with tools.chdir(source_folder):
            # configure.py
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "configure.py.patch"))
            print(
                "Build folder = {}, source is in {}, patch is {}".format(self.build_folder, source_folder, patch_file)
            )
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Tensorflow
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "tensorflow.BUILD.patch"))
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Boringssl
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "boringssl.BUILD.patch"))
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Protobuf
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "protobuf.BUILD.patch"))
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Grpc
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "grpc.BUILD.patch"))
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Aws Crypto
            patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "aws_crypto.cc.patch"))
            print("Applying patch {}".format(patch_file))
            tools.patch(patch_file=patch_file)

            # Jsoncpp if needed
            patching_jsoncpp = False
            if patching_jsoncpp:
                patch_file = os.path.realpath(os.path.join(self.build_folder, "patches", "jsoncpp.BUILD.patch"))
                print("Applying patch {}".format(patch_file))
                tools.patch(patch_file=patch_file)

    ################################################################################################################
    #
    ################################################################################################################
    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = dict()
            env_build["PYTHON_BIN_PATH"] = sys.executable
            env_build["USE_DEFAULT_PYTHON_LIB_PATH"] = "1"

            env_build["TF_NEED_GCP"] = "1" if self.options.need_gcp else "0"
            env_build["TF_NEED_CUDA"] = "1" if (self.options.need_cuda and not self.options.need_mkl) else "0"
            env_build["TF_DOWNLOAD_CLANG"] = "1" if self.options.download_clang else "0"
            env_build["TF_CUDA_CLANG"] = "1" if self.options.cuda_clang else "0"
            env_build["TF_NEED_HDFS"] = "1" if self.options.need_hdfs else "0"
            env_build["TF_NEED_OPENCL"] = "1" if self.options.need_opencl else "0"
            env_build["TF_NEED_JEMALLOC"] = "1" if self.options.need_jemalloc else "0"
            env_build["TF_ENABLE_XLA"] = "1" if self.options.enable_xla else "0"
            env_build["TF_NEED_VERBS"] = "1" if self.options.need_verbs else "0"
            env_build["TF_DOWNLOAD_MKL"] = "1" if self.options.download_mkl else "0"
            env_build["TF_NEED_MKL"] = "1" if (self.options.need_mkl and not self.options.need_cuda) else "0"
            env_build["TF_NEED_NGRAPH"] = "1" if self.options.need_ngraph else "0"
            env_build["TF_NEED_AWS"] = (
                "1" if self.options.need_aws else "0"
            )  # Does not work if AWS is set and we are putting in our own SSL
            env_build["TF_NEED_MPI"] = "1" if self.options.need_mpi else "0"
            env_build["TF_NEED_GDR"] = "1" if self.options.need_gdr else "0"
            env_build["TF_NEED_S3"] = "1" if self.options.need_s3 else "0"
            env_build["TF_NEED_OPENCL_SYCL"] = "1" if self.options.need_opencl_sycl else "0"
            env_build["TF_NEED_COMPUTECPP"] = "1" if self.options.need_computecpp else "0"
            env_build["TF_NEED_KAFKA"] = "1" if self.options.need_kafka else "0"
            env_build["TF_NEED_TENSORRT"] = "1" if (self.options.need_tensorrt and self.options.need_cuda) else "0"
            env_build["TF_NEED_IGNITE"] = "1" if self.options.need_ignite else "0"
            env_build["TF_NEED_ROCM"] = "1" if self.options.need_rocm else "0"

            env_build["TF_CONFIGURE_IOS"] = "1" if self.settings.os == "iOS" else "0"
            env_build["TF_SET_ANDROID_WORKSPACE"] = "1" if self.options.set_android_workspace else "0"
            env_build["TF_CONFIGURE_APPLE_BAZEL_RULES"] = "1"
            env_build["CC_OPT_FLAGS"] = "-march=native -Wno-sign-compare"
            env_build["GCC_HOST_COMPILER_PATH"] = (
                tools.which("clang") if self.options.cuda_clang else tools.which("gcc")
            )
            env_build["HOST_CXX_COMPILER"] = tools.which("clang++") if self.options.cuda_clang else tools.which("g++")

            # We want TF to use our versions of openssl, protobuf, and grpc
            self._add_lib_to_env("protobuf", "com_google_protobuf", env_build)
            self._add_lib_to_env("grpc", "grpc", env_build)
            self._add_lib_to_env("OpenSSL", "boringssl", env_build)

            # Patch the configure script and other files
            self._patch_tf_files()

            with tools.environment_append(env_build):
                self.run("python configure.py" if tools.os_info.is_windows else "./configure")
                self.run("bazel shutdown")

                bazel_config_flags = ""

                #                if (self.options.need_mkl and not self.options.need_cuda):
                #                    bazel_config_flags += "--config=mkl "

                if self.options.need_gdr:
                    bazel_config_flags += "--config=gdr "

                if self.options.need_verbs:
                    bazel_config_flags += "--config=verbs "

                if self.options.need_ngraph:
                    bazel_config_flags += "--config=ngraph "

                if self.options.need_numa:
                    bazel_config_flags += "--config=numa "

                if self.options.build_dynamic_kernels:
                    bazel_config_flags += "--config=build_dynamic_kernels "

                #                if (self.options.need_cuda and not self.options.need_mkl):
                #                    bazel_config_flags += "--config=cuda "

                if self.options.need_aws == False:
                    bazel_config_flags += "--config=noaws "

                if self.options.need_gcp == False:
                    bazel_config_flags += "--config=nogcp "

                if self.options.need_hdfs == False:
                    bazel_config_flags += "--config=nohdfs "

                optim_flags = ""
                safe_flags = ""
                os_name = str(self.settings.os).lower()

                if os_name == "macos":
                    optim_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = "-c opt --copt=-march=native"
                elif os_name == "linux":
                    optim_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = "-c opt"
                elif os_name == "windows":
                    optim_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = "-c opt --copt=-march=native --copt=-mfpmath=both"

                bazel_config_flags += optim_flags if self.options.build_optimized else safe_flags

                # This is a shite, ugly hack. Linking with devtoolset on Bazel is jacked: we need to link stdc++ statically
                # https://github.com/bazelbuild/bazel/issues/10327
                static_link_stdcpp = False
                if (os_name == "linux") and (
                    subprocess.check_output(["gcc", "-v"], encoding="UTF-8", stderr=subprocess.STDOUT).find(
                        "devtoolset"
                    )
                    != -1
                ):
                    print("build(): linking stdcpp statically on platform {}".format(platform.platform()))
                    static_link_stdcpp = True

                self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow_cc.so", static_link_stdcpp)

                self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow.so", static_link_stdcpp)

                self._build_bazel_target(bazel_config_flags, "//tensorflow/core:tensorflow", static_link_stdcpp)

                self._build_bazel_target(bazel_config_flags, "//tensorflow/c:c_api", static_link_stdcpp)

                self._build_bazel_target(
                    bazel_config_flags, "//tensorflow:libtensorflow_framework.so", static_link_stdcpp
                )

                self._build_bazel_target(bazel_config_flags, "//tensorflow/java:libtensorflow_jni", static_link_stdcpp)

                self._build_bazel_target(bazel_config_flags, "//tensorflow/java:tensorflow", static_link_stdcpp)

                self._build_bazel_target(
                    bazel_config_flags, "//tensorflow/core:framework_internal_impl", static_link_stdcpp
                )

                self._build_bazel_target(bazel_config_flags, "//tensorflow/cc:cc_ops", static_link_stdcpp)

                self._build_bazel_target(bazel_config_flags, "//tensorflow/cc:client_session", static_link_stdcpp)

                self._build_bazel_target(
                    bazel_config_flags, "//tensorflow/tools/graph_transforms:transform_utils", static_link_stdcpp
                )

                self._build_bazel_target(
                    bazel_config_flags, "//tensorflow/tools/graph_transforms:file_utils", static_link_stdcpp
                )

                self._build_bazel_target(bazel_config_flags, "//tensorflow:install_headers", static_link_stdcpp)
        return

    ################################################################################################################
    #
    ################################################################################################################
    def package(self):
        try:
            self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

            bazel_bin_directory = self._find_directory_under_directory(self._source_subfolder, "bazel-bin")[0]
            print("Absolute path of BAZEL-BIN directory: {}".format(os.path.abspath(bazel_bin_directory)))

            source_folder_path = os.path.realpath(self._source_subfolder)
            print("Absolute path of source_subfolder directory: {}".format(source_folder_path))

            inc_dir = os.path.realpath(os.path.join(self.package_folder, "include"))
            if not os.path.exists(inc_dir):
                print("Library directory {} does not exist, creating".format(inc_dir))
                os.makedirs(inc_dir)
            print("Real path of include directory: {}".format(inc_dir))

            # Copy the various TF Libs to their respective destiations
            lib_dir = os.path.abspath(os.path.join(self.package_folder, "lib"))
            if not os.path.exists(lib_dir):
                print("Library directory {} does not exist, creating".format(lib_dir))
                os.makedirs(lib_dir)
            print("Real path of lib directory: {}".format(lib_dir))

            self._copy_tf_libs(
                src_dir=os.path.abspath(os.path.join(bazel_bin_directory, "tensorflow")),
                dest_dir=lib_dir,
                search_patterns=["*.so", "*.dylib"],
            )

            os_name = str(self.settings.os).lower()
            if self.options.need_mkl:
                lib_ext = "dylib" if os_name == "macos" else "so"
                mkl_lib_name = (
                    "libmklml.{}".format(lib_ext) if os_name == "macos" else "libmklml_intel.{}".format(lib_ext)
                )
                mkl_lib = self._find_file(bazel_bin_directory, mkl_lib_name)
                if mkl_lib is not None:
                    self._copy_file(mkl_lib, lib_dir)

                iomp_lib_name = "libiomp5.{}".format(lib_ext)
                iomp_lib = self._find_file(bazel_bin_directory, iomp_lib_name)
                if iomp_lib is not None:
                    self._copy_file(iomp_lib, lib_dir)

            src_includes_dir = os.path.join(bazel_bin_directory, "tensorflow", "include")
            print("Copying absl includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "absl"), os.path.join(inc_dir, "absl"),
            )

            print("Copying Eigen includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "Eigen"), os.path.join(inc_dir, "Eigen"),
            )

            print("Copying unsupported includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "unsupported"), os.path.join(inc_dir, "unsupported"),
            )

            print("Copying TF includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "tensorflow"), os.path.join(inc_dir, "tensorflow"),
            )

            print("Copying thirdparty includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "third_party"), os.path.join(inc_dir, "third_party"),
            )

            print("Copying TF util includes")
            shutil.copytree(
                os.path.join(src_includes_dir, "util"), os.path.join(inc_dir, "util"),
            )

            print("Copying extra headers")
            # Copy extra headers
            self._copy_tf_extra_headers(
                os.path.join(source_folder_path, "tensorflow"), inc_dir, source_folder_path,
            )

            # Fix up pkgconfig file: this takes the tensorflow.pc.in file and generates tensorflow.pc
            pkg_config_dir = os.path.join(lib_dir, "pkgconfig")
            if not os.path.exists(pkg_config_dir):
                print("Pkgconfir directory {} does not exist, creating".format(pkg_config_dir))
                os.makedirs(pkg_config_dir)

            pkg_config_file = os.path.join(pkg_config_dir, "tensorflow.pc")
            source_folder_path = os.path.dirname(os.path.abspath(self._source_subfolder))

            shutil.copyfile(os.path.join(source_folder_path, "tensorflow.pc.in"), pkg_config_file)
            tools.replace_in_file(pkg_config_file, "@version@", self.version, strict=True)
            tools.replace_in_file(pkg_config_file, "@prefix@", lib_dir, strict=True)
        except Exception as inst:
            print("Exception caught packaging, fix error and re-run.")
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
        return

    ################################################################################################################
    #
    ################################################################################################################
    def package_info(self):
        self.cpp_info.libs = ["tensorflow"]
        return
