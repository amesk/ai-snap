#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

from .cli import cli

try:
    from .version import VERSION as __version__
except ModuleNotFoundError:
    __version__ = "0.0.1"

__author__ = "amesk <alexei.eskenazi@gmail.com>"
__license__ = "MIT"
__all__ = ["cli"]
