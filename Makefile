#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

ifeq ($(AI_SNAP_VERSION),)
    $(error AI_SNAP_VERSION environment variable is not defined, define it first!)
endif

.PHONY: build clean all

all:
	@echo Usage:
	@echo     make build
	@echo     make clean

build:
	pipenv run wheel $(AI_SNAP_VERSION)
	pipenv run exe $(AI_SNAP_VERSION)
	pipenv run changelog

clean:
	pipenv run clean
