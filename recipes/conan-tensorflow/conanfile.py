import os
import shutil
import sys
import contextlib
from pathlib import Path
import fnmatch
import functools
import itertools

from conans import ConanFile, tools
from conans.model.version import Version


class TensorFlowConan(ConanFile):
    name = "tensorflow"
    version = "2.1.0"
    homepage = "https://github.com/tensorflow/tensorflow"
    topics = ("conan", "tensorflow", "Machine Learning", "Neural Networks")
    url = "https://github.com/bincrafters/conan-tensorflow"
    description = "A Conan recipe to build Tensorflow C++ from code"
    author = "Prashanth Nandavanam <pn@forwardmeasure.com>"
    license = "Apache-2.0"
    _grpc_patch_file = "grpc_gettid.patch"
    exports = ["LICENSE.md", "tensorflow.pc.in", "tensorflow.pc"]
    exports_sources = [_grpc_patch_file, "tensorflow.pc.in", "tensorflow.pc"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
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
        "build_optimized": True,
        "build_monolithic": False,
        "build_dynamic_kernels": False,
        "need_gcp": False,
        "need_gdr": False,
        "need_cuda": False,
        "need_hdfs": False,
        "need_opencl": False,
        "need_jemalloc": False,
        "enable_xla": False,
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
    _grpc_version = "1.19.1"

    ################################################################################################################
    #
    ################################################################################################################
    def _find_grpc_src_dir(self, top_dir):
        # print("_find_grpc_src_dir(): top_dir = %s" % (top_dir))
        for (path, _, _) in os.walk(top_dir):
            base_name = os.path.basename(path)
            dir_name = os.path.dirname(path)
            inner_dir_name = os.path.basename(dir_name)
            print(
                "_find_grpc_src_dir(): base_name = %s, dir_name = %s, inner_dir_name = %s"
                % (base_name, dir_name, inner_dir_name)
            )

            if base_name == "src" and inner_dir_name == "grpc":
                inner_inner_dirname = os.path.basename(os.path.dirname(dir_name))
                if inner_inner_dirname == "external":
                    return os.path.dirname(path)
        return ""

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
    def _fix_grpc_version(self):
        """
        TF is usually bundled with really old versions of protobuf and gRPC. So, we cheekily
        upgarde them in place in the workspace the bazel before the build kicks off. We need
        to replace two things: the sha256 signature and the commit id of the particular version we want to use.
        sha256: Unfortunately at this point, I don't know how to get this value any other way than to install it using Conan
        commit id: Github keeps the commit ID of each PR that is approved, and you can pull specific commig IDs (standard git practice)
        You can check the checksums thus: shasum -a 1 grpc-1.25.0.zip* && shasum -a 256 grpc-1.25.0.zip
        """
        print("Fixing gRPC version...")
        bazel_workspace_path = os.path.realpath("tensorflow/workspace.bzl")
        print("Bazel workspace path = %s" % (bazel_workspace_path))

        # gRPC 1.25 github sha256 hash
        tools.replace_in_file(
            bazel_workspace_path,
            "67a6c26db56f345f7cee846e681db2c23f919eba46dd639b09462d1b6203d28c",
            "ffbe61269160ea745e487f79b0fd06b6edd3d50c6d9123f053b5634737cf2f69",
            strict=True,
        )

        # gRPC 1.25 github sha1 hash
        tools.replace_in_file(
            bazel_workspace_path,
            'strip_prefix = "grpc-4566c2a29ebec0835643b972eb99f4306c4234a3"',
            'strip_prefix = "grpc-1.25.0"',
            strict=True,
        )
        # gRPC 1.25 github sha1 hash
        tools.replace_in_file(
            bazel_workspace_path,
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/grpc/grpc/archive/4566c2a29ebec0835643b972eb99f4306c4234a3.tar.gz",
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/grpc/grpc/archive/v1.25.0.tar.gz",
            strict=True,
        )
        # gRPC 1.25 github sha1 hash
        tools.replace_in_file(
            bazel_workspace_path,
            "https://github.com/grpc/grpc/archive/4566c2a29ebec0835643b972eb99f4306c4234a3.tar.gz",
            "https://github.com/grpc/grpc/archive/v1.25.0.tar.gz",
            strict=True,
        )

    ################################################################################################################
    #
    ################################################################################################################
    def _fix_protobuf_version(self):
        """
        TF is usually bundled with really old versions of protobuf and gRPC. So, we cheekily
        upgarde them in place in the workspace the bazel before the build kicks off. We need
        to replace two things: the sha256 signature and the commit id of the particular version we want to use.
        sha256: Unfortunately at this point, I don't know how to get this value any other way than to install it using Conan
        commit id: Github keeps the commit ID of each PR that is approved, and you can pull specific commit IDs.
        The version of gRPC can be found in the file: gRPC.podspec under the extracted source.
        """
        print("Fixing protobuf version...")
        bazel_workspace_path = os.path.realpath("tensorflow/workspace.bzl")
        print("Bazel workspace path = %s" % (bazel_workspace_path))

        # Protobuf 3.10.1 github sha256 hash
        tools.replace_in_file(
            bazel_workspace_path,
            "b9e92f9af8819bbbc514e2902aec860415b70209f31dfc8c4fa72515a5df9d59",
            "632c4ba94cd9c684cb1b7b9644f796209ae5b73dd440221a23c7fb334d51fb81",
            strict=True,
        )
        # Protobuf 3.10.1 github commit id
        tools.replace_in_file(
            bazel_workspace_path,
            "310ba5ee72661c081129eb878c1bbcec936b20f0",
            "d09d649aea36f02c03f8396ba39a8d4db8a607e4",
            strict=True,
        )
        # Remove call to patch protobuf
        tools.replace_in_file(
            bazel_workspace_path, "        patch_file = clean_dep(PROTOBUF_PATCH),\n", "", strict=True,
        )
        tools.replace_in_file(
            bazel_workspace_path, "sha256 = PROTOBUF_SHA256", "        sha256 = PROTOBUF_SHA256,", strict=True,
        )
        return

    ################################################################################################################
    #
    ################################################################################################################
    def _patch_grpc(self, bazel_cache_dir):
        # Determine where to find the grpc sources
        grpc_source_dir = self._find_grpc_src_dir(bazel_cache_dir)

        # Copy patch file
        source_folder_path = os.path.dirname(os.path.abspath(self._source_subfolder))
        # print("Source folder = %s" % (source_folder_path))
        grpc_patch_file_path = os.path.realpath(os.path.dirname(source_folder_path) + os.sep + self._grpc_patch_file)
        # print("Copying %s to %s" % (grpc_patch_file_path, grpc_source_dir))
        shutil.copy(grpc_patch_file_path, grpc_source_dir)
        grpc_patch_file_path = os.path.realpath(grpc_source_dir + os.sep + self._grpc_patch_file)

        # print("Patching grpc source %s using %s" % (grpc_source_dir, grpc_patch_file_path))
        tools.patch(base_path=grpc_source_dir, patch_file=grpc_patch_file_path)

        return

    ################################################################################################################
    #
    ################################################################################################################
    def _build_bazel_target(self, bazel_config_flags, target):
        self.run(
            "bazel --output_user_root=%s --host_jvm_args=-Xms512M --host_jvm_args=-Xmx8192M build --jobs 12 --incompatible_no_support_tools_in_action_inputs=false --nodiscard_analysis_cache --keep_state_after_build --track_incremental_state --verbose_failures %s %s"
            % (self._bazel_cache_dir, bazel_config_flags, target)
        )

    ################################################################################################################
    #
    ################################################################################################################
    @contextlib.contextmanager
    def _pushd(self, new_dir):
        previous_dir = os.getcwd()
        os.chdir(new_dir)
        yield
        os.chdir(previous_dir)

    ################################################################################################################
    #
    ################################################################################################################
    def _copy_file(self, src_file, dest_dir, verbose=True):
        print("Copying %s to %s" % (src_file, dest_dir))
        if not os.path.isfile(src_file):
            print("Source %s must be a file" % (src_file))
            return

        if not os.path.isdir(dest_dir):
            print("Destination must be a directory and not a file")
            return

        dest_file = os.path.join(dest_dir, os.path.basename(src_file))
        print("Copying %s as %s" % (src_file, dest_file))

        if os.path.islink(src_file):
            # If the destinantion file exists as a link, unlink
            if os.path.lexists(dest_file):
                os.unlink(dest_file)

            # Step down one level of indirection
            linkto = os.readlink(src_file)
            linkto_dest = os.path.join(os.path.dirname(src_file), os.path.basename(linkto))

            print("%s links to %s (abs %s)" % (src_file, linkto, linkto_dest))

            # Recurse and get the link target
            dest = self._copy_file(linkto_dest, dest_dir, verbose)
            os.symlink(dest, os.path.join(dest_dir, os.path.basename(src_file)))

            return dest_file
        else:
            shutil.copy(src_file, dest_dir)
            print("Returning %s" % (dest_file))
            return dest_file

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
                "_copy_tf_libs(): copying file matching patterns %s from %s to %s"
                % (str(search_patterns), src_dir, dest_dir)
            )

            for f in self._find_files(src_dir=src_dir, search_patterns=search_patterns):
                print("Copying %s to %s" % (f, dest_dir))
                self._copy_file(f, dest_dir, verbose=True)

        except Exception as inst:
            print("Exception caught copying tf libs")
            print(inst)

    ################################################################################################################
    #
    ################################################################################################################
    def _copy_tf_libs_old(self, src_dir, dest_dir, search_patterns=None):
        try:
            if search_patterns is None:
                search_patterns = ["*.so"]

            print(
                "_copy_tf_libs(): copying file matching patterns %s from %s to %s"
                % (str(search_patterns), src_dir, dest_dir)
            )
            for f in self._find_files(src_dir=src_dir, search_patterns=search_patterns):
                print("Copying %s to %s" % (f, dest_dir))
                self._copy_file(f, dest_dir, verbose=True)

            # If we are on Mac, copy inidvidual files, since wildcarding on *.dylib ended up in an infinite loop
            os_name = str(self.settings.os).lower()
            if os_name == "macos":
                tf_framework_dylib = (
                    os.path.join(src_dir, "tensorflow", "libtensorflow_framework.1.dylib")
                    if self.version < Version("2.0.0")
                    else os.path.join(src_dir, "tensorflow", "libtensorflow_framework.2.dylib")
                )
                print("Copying %s to %s" % (tf_framework_dylib, dest_dir))
                self._copy_file(tf_framework_dylib, dest_dir, verbose=True)

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
    def build_requirements(self):
        if not tools.which("bazel"):
            self.build_requires("bazel_installer/0.29.1@bincrafters/stable")

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
        sha256 = "49b5f0495cd681cbcb5296a4476853d4aea19a43bdd9f179c928a977308a0617"
        archive_name = "master"
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, archive_name))
        extracted_dir = self.name + "-" + archive_name
        os.rename(extracted_dir, self._source_subfolder)
        print("Downloaded archive from %s to %s" % (self.homepage, extracted_dir))

    ################################################################################################################
    #
    ################################################################################################################
    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = dict()
            env_build["PYTHON_BIN_PATH"] = sys.executable
            env_build["USE_DEFAULT_PYTHON_LIB_PATH"] = "1"

            env_build["TF_NEED_GCP"] = "1" if self.options.need_gcp else "0"
            env_build["TF_NEED_CUDA"] = "1" if self.options.need_cuda else "0"
            env_build["TF_DOWNLOAD_CLANG"] = "0"
            env_build["TF_NEED_HDFS"] = "1" if self.options.need_hdfs else "0"
            env_build["TF_NEED_OPENCL"] = "1" if self.options.need_opencl else "0"
            env_build["TF_NEED_JEMALLOC"] = "1" if self.options.need_jemalloc else "0"
            env_build["TF_ENABLE_XLA"] = "1" if self.options.enable_xla else "0"
            env_build["TF_NEED_VERBS"] = "1" if self.options.need_verbs else "0"
            env_build["TF_DOWNLOAD_MKL"] = "1" if self.options.download_mkl else "0"
            env_build["TF_NEED_MKL"] = "1" if self.options.need_mkl else "0"
            env_build["TF_NEED_NGRAPH"] = "1" if self.options.need_ngraph else "0"
            env_build["TF_NEED_AWS"] = "1" if self.options.need_aws else "0"
            env_build["TF_NEED_MPI"] = "1" if self.options.need_mpi else "0"
            env_build["TF_NEED_GDR"] = "1" if self.options.need_gdr else "0"
            env_build["TF_NEED_S3"] = "1" if self.options.need_s3 else "0"
            env_build["TF_NEED_OPENCL_SYCL"] = "1" if self.options.need_opencl_sycl else "0"
            env_build["TF_NEED_COMPUTECPP"] = "1" if self.options.need_computecpp else "0"
            env_build["TF_NEED_KAFKA"] = "1" if self.options.need_kafka else "0"
            env_build["TF_NEED_TENSORRT"] = "1" if (self.options.need_tensorrt and self.options.need_cuda) else "0"
            env_build["TF_NEED_IGNITE"] = "1" if self.options.need_ignite else "0"
            env_build["TF_NEED_ROCM"] = "1" if self.options.need_rocm else "0"

            env_build["CC_OPT_FLAGS"] = "/arch:AVX" if self.settings.compiler == "Visual Studio" else "-march=native"
            env_build["TF_CONFIGURE_IOS"] = "1" if self.settings.os == "iOS" else "0"
            env_build["TF_SET_ANDROID_WORKSPACE"] = "1" if self.options.set_android_workspace else "0"
            env_build["TF_CONFIGURE_APPLE_BAZEL_RULES"] = "1"

            with tools.environment_append(env_build):
                self.run("python configure.py" if tools.os_info.is_windows else "./configure")
                self.run("bazel shutdown")

                bazel_config_flags = ""

                if self.options.need_mkl:
                    bazel_config_flags += "--config=mkl "

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

                if self.options.need_cuda == True:
                    bazel_config_flags += "--config=cuda"

                os_name = str(self.settings.os).lower()

                optim_flags = ""
                safe_flags = ""
                if os_name == "macos":
                    optim_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = ""
                elif os_name == "linux":
                    optim_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = "-c opt --copt=-march=native --copt=-mfpmath=both"
                elif os_name == "windows":
                    opt_flags = "-c opt --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.1 --copt=-msse4.2"
                    safe_flags = "-c opt --copt=-march=native --copt=-mfpmath=both"

                bazel_config_flags = optim_flags if self.options.build_optimized else safe_flags

                try:
                    print("Attempting to build libtensorflow_cc BEFORE patch")
                    self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow_cc.so")
                except Exception as inst:
                    print("Exception caught building libtensorflow_cc, attempting to PATCH")
                    print(inst)

                    if self._grpc_version < Version("1.22.0"):
                        # Patch gRPC before proceeding
                        # TF uses OLD versions: gRPC V1.19.1 and protobuf 3.8.0
                        self._patch_grpc(self._bazel_cache_dir)
                    else:
                        # Fix up the gRPC version
                        self._fix_grpc_version()

                    self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow_cc.so")

                self._build_bazel_target(bazel_config_flags, "//tensorflow/core:tensorflow")

                self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow.so")

                self._build_bazel_target(bazel_config_flags, "//tensorflow/c:c_api")

                self._build_bazel_target(bazel_config_flags, "//tensorflow:libtensorflow_framework.so")

                self._build_bazel_target(bazel_config_flags, "//tensorflow/java:tensorflow")
                self._build_bazel_target(bazel_config_flags, "//tensorflow/java:libtensorflow_jni")

                self._build_bazel_target(bazel_config_flags, "//tensorflow/core:framework_internal_impl")
                self._build_bazel_target(bazel_config_flags, "//tensorflow/core:tensorflow")
                self._build_bazel_target(bazel_config_flags, "//tensorflow/cc:cc_ops")

                self._build_bazel_target(bazel_config_flags, "//tensorflow/cc:client_session")

                self._build_bazel_target(
                    bazel_config_flags, "//tensorflow/tools/graph_transforms:transform_utils",
                )

                self._build_bazel_target(bazel_config_flags, "//tensorflow/tools/graph_transforms:file_utils")

                self._build_bazel_target(bazel_config_flags, "//tensorflow:install_headers")
        return

    ################################################################################################################
    #
    ################################################################################################################
    def package(self):
        try:
            self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

            bazel_bin_directory = self._find_directory_under_directory(self._source_subfolder, "bazel-bin")[0]
            print("Absolute path of BAZEL-BIN directory: %s" % os.path.abspath(bazel_bin_directory))

            source_folder_path = os.path.realpath(self._source_subfolder)
            print("Absolute path of source_subfolder directory: %s" % (source_folder_path))

            inc_dir = os.path.realpath(os.path.join(self.package_folder, "include"))
            if not os.path.exists(inc_dir):
                print("Library directory %s does not exist, creating" % (inc_dir))
                os.makedirs(inc_dir)
            print("Real path of include directory: %s" % (inc_dir))

            # Copy the various TF Libs to their respective destiations
            lib_dir = os.path.abspath(os.path.join(self.package_folder, "lib"))
            if not os.path.exists(lib_dir):
                print("Library directory %s does not exist, creating" % (lib_dir))
                os.makedirs(lib_dir)
            print("Real path of lib directory: %s" % (lib_dir))

            self._copy_tf_libs(
                src_dir=os.path.abspath(os.path.join(bazel_bin_directory, "tensorflow")),
                dest_dir=lib_dir,
                search_patterns=["*.so", "*.dylib", "*.params"],
            )

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
                print("Pkgconfir directory %s does not exist, creating" % (pkg_config_dir))
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
