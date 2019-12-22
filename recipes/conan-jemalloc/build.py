#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from bincrafters import build_template_installer
from bincrafters import build_shared
from bincrafters import build_template_default

from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="jmalloc:shared")
    builder.run()
