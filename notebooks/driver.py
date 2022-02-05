#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:25:14 2022

@author: cgwork
"""

import os

from container import MediaContainer, load_mc, save_mc
from media import Media
from options import Options
from encoder import Encoder
from video_quality_tests import VideoQualityTests

# to create a container

md = Media()
# inputdir = md.input_dir()
md.glob_media() # glob all files into list, seen by md.input_files()

class MediaTests:

    def __init__(self):
        self.__md = Media()
        self.__options = Options()
        self.__encoder = Encoder()
        self.__vq = VideoQualityTests()
        self.__mc = MediaContainer()

    def feed_media(self):
        self.__md.

