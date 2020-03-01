#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
from conans import tools
import platform
import os

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)

    # skip shared build on Windows + GCC (ranges doesn't work)
    if tools.os_info.is_windows and os.getenv("MINGW_CONFIGURATIONS"):
        filtered_builds = []
        for settings, options, env_vars, build_requires, reference in builder.items:
            if not options["fmt:shared"]:
                filtered_builds.append([settings, options, env_vars, build_requires])
        builder.builds = filtered_builds

    # Add one extra build to create a header-only version
    if tools.os_info.is_linux and os.getenv("CONAN_GCC_VERSIONS", False) == "6.3":
        builder.add({}, {"fmt:header_only" : True}, {}, {})

    builder.run()
