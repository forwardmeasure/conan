#!/usr/bin/env python

from bincrafters import build_template_default, build_template_installer, build_shared
from conans import tools
import os

# installer might depend on lib or vice versa. Make sure that the dependecy is available and up-to-date
build_policy = os.getenv("CONAN_BUILD_POLICY", "outdated")
os.environ["CONAN_BUILD_POLICY"] = build_policy

if __name__ == "__main__":
    docker_entry_script = ".ci/entry.sh"
    docker_entry_installer_script = ".ci/entry_installer.sh"

    if "CONAN_CONANFILE" in os.environ and os.environ["CONAN_CONANFILE"] == "conanfile_installer.py":
        arch = os.environ["ARCH"]
        builder = build_template_installer.get_builder(docker_entry_script=docker_entry_installer_script)
        builder.add({"os": build_shared.get_os(), "arch_build": arch, "arch": arch}, {}, {}, {})
        builder.run()
    else:
        builder = build_template_default.get_builder(docker_entry_script=docker_entry_script, pure_c=False)
        builder.run()
