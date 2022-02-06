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
        # an interface to change the options should be provided later
        # the same for some encoder sets
        self.__options = Options()
        self.__encoder = Encoder(self.__md, self.__options)
        #self.__vq = VideoQualityTests()
        # this is just the final container for the assembled data
        self.__mc = MediaContainer()

    @property
    def media_container(self):
        return self.__mc

    @media_container.setter
    def media_container(self, mc):
        if mc is not None and isinstance(mc, MediaContainer):
            self.__mc = mc

    def prepare_media(self, indir=None, outdir=None, options=None) -> None:

        if indir is not None and os.path.isdir(indir):
            self.__md.input_dir = indir
        if outdir is not None and os.path.isdir(outdir):
            self.__md.output_dir = outdir

        if options is not None and isinstance(options, Options):
            self.__options = options

        # gather all the input under inputdir
        self.__md.glob_media()
        # store the ffprobe data structure
        self.__mc.inputdir = self.__md.input_dir
        self.__md.inputdata = self.__md.probe_all()
        self.__populate_outputs()

    def __populate_outputs(self) -> None:
        # foreach basename, the iterated codecs
        # self.__mc.outputdata = {
        #    os.path.split(k)[1]: {
        #        vcodec: {} for vcodec in self.__options.codecs()["videocodecs"]
        #    } for k in tmp}

        # For dataviz, we can at least do this:
        # Narrow easily by basename, by codec type, and by parameter variation
        # and for this, we can choose a case and check the metrics

        # op = options instance
        # paramsets = {j:{} for j in op.encoding_sets().keys()}
        # vcodec = {j:paramsets for j in op.codecs()["videocodecs"]}
        # ec = encoder instance
        # basename = {os.path.split(k)[1]:vcodec for \
        #    k in md.output_files()}
        #
        # mc.outputdata = {basename : {vcodec : {paramsets : fqn } } }
        #
        # fqn = within paramset, the FQN for the variation in the list
        # when you build paramsets, it is the list in values
        # so, you can build here a simpler version
        # basename_paramset_setting
        #
        # Encoder.fqn(basename) returns [paramset[fqn], ...]
        # you must iterate over the paramsets
        # so, instead of
        # paramsets = {j:{} for j in op.encoding_sets().keys()}
        #
        # paramsets = {key:
        #    [
        #        build_fname(op.encode_options, key, values, basename)
        #    ]
        #    for key, values in op.encoding_sets().items()}
        #
        # and build_fname(encode_options, key, values, basename)
        # returns an item of the list associated w param set key
        #
        # for val in values:
        #    encode_options[key] = val
        #    fname_suffix = "__".join(map(lambda x, y: x + "_" + str(y),
        # encode_options().keys(), op.encode_options().values()
        #
        self.__mc.outputdata = {
            os.path.split(outfile)[1]: {
                vcodec: {
                    paramset: self.__encoder.build_fname(
                        paramset, setvals, os.path.split(outfile)[1]) for
                    paramset, setvals in
                    self.__options.encoding_sets().items()
                } for vcodec in self.__options.codecs()["videocodecs"]
            } for outfile in self.__md.output_files()}
        # which leads us to the FQN names
