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

    def __init__(self, indir = None, outdir = None):

        self.__md = Media()
        if indir is not None and os.path.isdir(indir):
            self.__md.input_dir = indir
        if outdir is not None and os.path.isdir(outdir):
            self.__md.output_dir = outdir

        self.__options = Options()
        self.__encoder = Encoder()
        self.__vq = VideoQualityTests()
        self.__mc = MediaContainer()

    def feed_media(self, indir = None):
        if indir is not None and os.path.isdir(indir):
            self.__md.input_dir = indir

        self.__md.glob_media()
        # and store the input dir, and the nested input src : ffprobe data
        # into the media container.
        #infiles = self.__md.input_files()
        #indata = self.__md.probe_all()
        self.__mc.inputdir = self.__md.input_dir
        self.__mc.inputdata = self.__md.probe_all()

    def prepare_output(self, outdir = None):
        if outdir is not None and os.path.isdir(outdir):
            self.__md.output_dir = outdir

        self.__mc.outputdir = self.__md.output_dir
        self.__mc.outputdata = {k:{} for k in self.__md.output_files()}



