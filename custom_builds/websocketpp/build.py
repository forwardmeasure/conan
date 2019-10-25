#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from bincrafters import build_template_installer
from bincrafters import build_shared
from bincrafters import build_template_default

if __name__ == "__main__":

    arch = os.environ["ARCH"]
    builder = build_template_installer.get_builder()
    builder.add({"os" : build_shared.get_os(), "arch_build" : arch}, {}, {}, {})
    builder.run()
