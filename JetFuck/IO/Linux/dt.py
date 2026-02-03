# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# =============================================================================
# MODIFICATION NOTICE
# =============================================================================
# Author: VoxVoltera
# Date: 2026-02-03
#
# Purpose:
#   This file has been modified for academic and experimental purposes.
#   The modifications are intended to support research, prototyping, and
#   system bring-up on NVIDIA Jetson Nano hardware in non-standard or
#   constrained software environments.
#
# Summary of Modifications:
#   - Disabled strict board compatibility and model matching logic.
#   - Forced selection of a known-correct Jetson Nano Developer Kit (B00) DTB.
#   - Prevented fatal termination when board auto-detection fails.
#   - Bypassed hardware identification checks that are unreliable on
#     customized or partially-upgraded JetPack / L4T images.
#   - Converted several hard-failure paths into safe fallbacks to allow
#     Jetson-IO tooling to run deterministically.
#
# Rationale:
#   During our acedemic research project, the jetson nano image ended up
#   being modified to a great extend, to get 2026 compiled webservers
#   and computer vision algorithms running. This means that a great number
#   of inbuilt nvidia functions either broke or got corrupted, including \
#   dts and FDT loading
#
# Disclaimer:
#   These modifications are NOT intended for production systems.
#   They intentionally relax safety and validation checks.
#   Use at your own risk.
#
# Original copyright notices are preserved below.
# =============================================================================

IGNORE_EEPROM_ERRORS = True

from Utils import fio
import os


def read_prop(prop):
    path = '/sys/firmware/devicetree/base'
    node = os.path.join(path, prop)
    fio.is_readable(node)

    with open(node, 'r') as f:
        value = f.readline()

    # Return a string of values with a single space delimiter.
    # Note this is equivalent behaviour to the 'fdtget' tool.
    return ' '.join(value.split('\0')).rstrip()
