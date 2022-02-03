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
encoder = enc.Encoder(media, options)

# debug the output files
#encoder.encoding(media.input_files()[0], media.output_files()[0])
#encoder.encode_videos()
#encoder.encode_video(
#    media.input_files()[0],
#    media.output_files()[0],
#    {
#        **options.common_options(),
#        **options.encode_options()
#    },
#    debug=False)

# encode videos encodes all from media input, and
# compressed with full qualified names into media output dir


