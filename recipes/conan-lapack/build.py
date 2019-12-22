#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import copy
from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds()
    if os.getenv("BUILD_VISUAL_STUDIO"):
        builder.remove_build_if(lambda build: not build.options["lapack:shared"])
        builder.update_build_if(lambda build: True, new_options={"lapack:visual_studio": True})
    builder.run()