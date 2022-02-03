#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 14:03:23 2022

@author: cgwork
"""

import os


import encoder as enc
import media as md
import options as op

# default input dir defined by VIDEO_RESOURCES
# default compressed video dir VIDEO_COMPRESSED
# one can inspect and siet via media.config() dictionary
# which contains "original_dir" and "compressed_dir" entries
#
media = md.Media()
# glob all media in VIDEO_RESOURCES or overriden input dir
media.glob_media()

#print(media.input_files())
#info = media.info()

# Create an options container
options = op.Options()

# now create an encoder instance that will contain both
# the media objects and the encoder options


