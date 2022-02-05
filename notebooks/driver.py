#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:25:14 2022

@author: cgwork
"""

import os

from container import (Codec, MediaContainer, MediaInfo, OutputBasename,
                       Parameters, QualifiedOutput, VideoQuality, load_mc,
                       save_mc)
from encoder import Encoder
from media import Media
from options import Options
from video_quality_tests import VideoQualityTests

# to create a container

md = Media()
# inputdir = md.input_dir()
md.glob_media()  # glob all files into list, seen by md.input_files()


class MediaTests:

    def __init__(self, indir=None, outdir=None):

        self.__md = Media()
        if indir is not None and os.path.isdir(indir):
            self.__md.input_dir = indir
        if outdir is not None and os.path.isdir(outdir):
            self.__md.output_dir = outdir

        self.__options = Options()
        self.__encoder = Encoder(self.__md, self.__options)
        #self.__vq = VideoQualityTests()
        self.__mc = MediaContainer()

    # start preparing the mc container, first with the src media and ff data
    def feed_media(self, indir=None) -> None:
        if indir is not None and os.path.isdir(indir):
            self.__md.input_dir = indir

        self.__md.glob_media()
        # and store the input dir, and the nested input src : ffprobe data
        # into the media container.
        #infiles = self.__md.input_files()
        #indata = self.__md.probe_all()
        self.__mc.inputdir = self.__md.input_dir
        self.__mc.inputdata = self.__md.probe_all()

    # now the base outputnames and the base structure for the compressed files
    def prepare_output(self, outdir=None) -> None:
        if outdir is not None and os.path.isdir(outdir):
            self.__md.output_dir = outdir

        self.__mc.outputdir = self.__md.output_dir
        # note, for dataframes, metrics, we might get by without the
        # full path and basename.
        # but since we already did it in encoder.qualify_output_files()
        self.__encoder = Encoder(self.__md, self.__options)

        tmp = self.__encoder.qualify_output_files()
        # foreach basename, the iterated codecs
        # self.__mc.outputdata = {
        #    os.path.split(k)[1]: {
        #        vcodec: {} for vcodec in self.__options.codecs()["videocodecs"]
        #    } for k in tmp}

        # foreach dict( str : list ) of encoder options
        # you only need the parameter set, the keys, since the rest is FQN
        # output name
        # TODO: MOVE ALL of this into the classes, since dataclasses can
        #       have regular methods.
        # BIG TODO ^^^
        #
        # For dataviz, we can at least do this:
        # Narrow easily by basename, by codec type, and by parameter variation
        # and for this, we can choose a case and check the metrics

        # op = options instance
        # paramsets = {j:{} for j in op.encoding_sets().keys}
        # vcodec = {j:paramsets for j in op.codecs()["videocodecs"]}
        # ec = encoder instance
        # basename = {os.path.split(k)[1]:vcodec for \
        #    k in ec.qualify_output_files()}


        self.__mc.outputdata = {
            os.path.split(k)[1]: {
                vcodec: {
                    j: {} for j in self.__options.encoding_sets().keys()
                } for vcodec in self.__options.codecs()["videocodecs"]
            } for k in tmp}
        # which leads us to the FQN names


    def mc_storage(self):
        return self.__mc
