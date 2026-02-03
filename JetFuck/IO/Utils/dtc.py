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


from Utils import syscall
import glob
import os


def __files_exist(*files):
    for f in files:
        if os.path.exists(f) is False:
            raise RuntimeError("File %s not found!" % f)


def __prop_exists(dtb, node, prop):
    return syscall.call('fdtget "%s" "%s" "%s"' % (dtb, node, prop))


def extract(dtb, dts):
    __files_exist(dtb)
    if syscall.call('dtc -I dtb -O dts "%s" -o "%s"' % (dtb, dts)):
        raise RuntimeError("Failed to extract %s to %s!" % (dtb, dts))


def compile(dts, dtb):
    __files_exist(dts)
    if syscall.call('dtc -I dts -O dtb "%s" -o "%s"' % (dts, dtb)):
        raise RuntimeError("Failed to compile %s to %s!" % (dts, dtb))


def overlay(dtb, out, *overlays):
    for overlay in overlays:
        __files_exist(dtb, overlay)
    files = ' '.join(overlays)
    if syscall.call('fdtoverlay -i "%s" -o "%s" "%s"' % (dtb, out, files)):
        raise RuntimeError("Failed to overlay %s with %s!" % (dtb, files))


def get_child_nodes(dtb, node):
    __files_exist(dtb)
    return syscall.call_out('fdtget -l "%s" "%s"' % (dtb, node))


def get_child_props(dtb, node):
    __files_exist(dtb)
    return syscall.call_out('fdtget -p "%s" "%s"' % (dtb, node))


def get_compatible(dtb):
    return get_prop_value(dtb, '/', 'compatible', 0)


def get_model(dtb):
    return get_prop_value(dtb, '/', 'model', 0)


def get_prop_value(dtb, node, prop, index):
    __files_exist(dtb)
    if __prop_exists(dtb, node, prop):
        return None
    values = syscall.call_out('fdtget "%s" "%s" "%s"' % (dtb, node, prop))
    if index >= len(values):
        return None
    return values[index]


def set_prop_value(dtb, node, dtype, prop, value):
    __files_exist(dtb)
    if syscall.call('fdtput -t "%s" "%s" "%s" "%s" "%s"' %
                    (dtype, dtb, node, prop, value)):
        raise RuntimeError("Failed to get property value for %s%s!" %
                           (node, prop))


def find_nodes_with_prop(dtb, node, prop):
    match = []
    cnodes = get_child_nodes(dtb, node)
    for cnode in cnodes:
        cpath = "%s%s/" % (node, cnode)
        match.extend(find_nodes_with_prop(dtb, cpath, prop))
        props = get_child_props(dtb, cpath)
        if prop in props:
            match.append(cpath)
    return match


# ------------------------------------------------------------------
# HARD-FORCED DTB SELECTION (OPTION A + ABSOLUTE FALLBACK)
# ------------------------------------------------------------------
def find_compatible_dtb_files(compat, model, path):
    """
    Force Jetson Nano devkit b00 DTB and ignore compat/model.
    This makes Jetson-IO stop failing board detection on images where
    the running DT reports only generic compatible strings.
    """
    forced = os.path.join(path, 'kernel_tegra210-p3448-0000-p3449-0000-b00.dtb')
    if os.path.exists(forced):
        return [forced]

    # Fallback: return any DTB present
    dtbs = sorted(glob.glob(os.path.join(path, '*.dtb')))
    return dtbs if dtbs else None


def find_compatible_dtbo_files(compat, path):
    dtbos = []
    for dtbo in glob.glob(os.path.join(path, '*.dtbo')):
        c = get_compatible(dtbo)
        if c is None:
            continue
        if compat in c:
            dtbos.append(dtbo)
    if not dtbos:
        return None
    return dtbos


def remove_node(dtb, node):
    __files_exist(dtb)
    return syscall.call('fdtput -r "%s" "%s"' % (dtb, node))


if syscall.call('which dtc') or syscall.call('which fdtoverlay') or \
   syscall.call('which fdtget') or syscall.call('which fdtput'):
    raise RuntimeError("Device-tree compiler not found!")
