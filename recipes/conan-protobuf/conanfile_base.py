from conans import ConanFile, tools
import os


class ConanFileBase(ConanFile):
    _base_name = "protobuf"
    version = "3.12.1"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md", "conanfile_base.py"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        sha256 = "cb9b3f9d625b5739a358268eb3421de11cacd90025f5f7672c3930553eca810e"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self._base_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
