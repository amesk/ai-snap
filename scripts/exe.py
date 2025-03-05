#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

import re, os, sys

from os.path import (
    join,
    dirname,
    realpath,
)

root_dir = realpath(join(dirname(__file__), ".."))

def replace_version(version):
    script_filename = join(root_dir, "ai_snap", "version.py")
    filedata = 'VERSION = "{}"'.format(version)
    with open(script_filename, "wb") as file:
        file.write(filedata.encode("utf-8"))
        
def replace_toml_version(version):
    filename = join(root_dir, "pyproject.toml")
    with open(filename, "rb") as file:
        filedata = file.read().decode("utf-8")

    # Replace the target string
    filedata = re.sub(r'version = ".*"', 'version = "{}"'.format(version), filedata)

    # Write the file out again
    with open(filename, "wb") as file:
        file.write(filedata.encode("utf-8"))

if __name__ == "__main__":
    if os.getcwd() != root_dir:
        print("Please run from root directory")
        sys.exit(1)
    

    version = sys.argv[1] if len(sys.argv) >= 2 else os.environ.get("VERSION")
    
    if not version:
        app = sys.argv[0]
        print(f"Usage: {app} <version>, or set VERSION environment variable")
        sys.exit(1)
        
    
    replace_version(version)
    replace_toml_version(version)
    os.system(f"pyinstaller -F --name ai-snap.exe ai-snap.py")
