#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 16:25:14 2022

@author: cgwork
"""

import json
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
        self.__videoqt = VideoQualityTests()
        #self.__vq = VideoQualityTests()
        # this is just the final container for the assembled data
        self.__mc = {}  # MediaContainer()
        self.__populated = False
        self.__io_files_list = None

    @property
    def media_container(self):
        return self.__mc

    @media_container.setter
    def media_container(self, mc):
        if mc is not None and isinstance(mc, MediaContainer):
            self.__mc = mc

    @property
    def outputdata(self):
        return self.__mc["outputdata"]

    @outputdata.setter
    def outputdata(self, outputdata):
        self.__mc["outputdata"] = outputdata

    # add interface to options here
    # this encodes only one codec
    # add method to iterate over codecs
    def encode_videos(self, debug=True, progress=False):
        self.__encoder.encode_videos(debug=debug, progress=progress)

    @property
    def options(self):
        return self.__options

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
        self.__mc["inputdir"] = self.__md.input_dir
        self.__mc["inputdata"] = self.__md.probe_all()
        self.__mc["outputdir"] = self.__md.output_dir
        self.__populate_outputs()
        # some sanitization to catch issues earlier, though empty output
        # data would be pretty obvious
        self.__populated = len(self.__mc["outputdata"].values()) > 0

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
        self.__mc["outputdata"] = {
            os.path.split(outfile)[1]: {
                vcodec: {
                    paramset: self.__encoder.fqn(os.path.split(outfile)[1]) for
                    paramset, setvals in
                    self.__options.encoding_sets().items()
                } for vcodec in self.__options.codecs()["videocodecs"]
            } for outfile in self.__md.output_files()}
        # which leads us to the FQN names

    def save(self, filename, overwrite=False):
        #save_mc(self.__mc, filename, overwrite)
        if overwrite is False and os.path.exists(filename):
            raise FileExistsError

        with open(filename, "w") as jsonfile:
            json.dump(self.media_container, jsonfile, indent=4)
            #json.write(self.media_container, jsonfile)

    def load(self, filename):
        #self.__mc = load_mc(filename)
        if not os.path.exists(filename):
            raise IOError

        data = {}
        with open(filename, "r") as jsonfile:
            data = json.load(jsonfile)
        return data

    # with "outputdata" property, we can chain successive filters
    @staticmethod
    def od_by_file(outputdata, fname):
        if fname is None or not isinstance(fname, str) \
                or not fname in outputdata.keys():
            return outputdata
        return {k: v for k, v in outputdata.items() if fname in k}

    @staticmethod
    def od_by_codec(outputdata, codec):
        if codec is None or not isinstance(codec, str):
            return outputdata
        return {k: v for k, v in outputdata.items() if codec in v.keys()}

    @staticmethod
    def od_by_paramset(outputdata, paramset):
        if paramset is None or not isinstance(paramset, str):
            return outputdata
        return {
            k: {i: j for i, j in v.items() if paramset in j.keys()}
            for k, v in outputdata.items()
        }

    @staticmethod
    def od_by_fqn_output(outputdata, outputname):
        if outputname is None or not isinstance(outputname, str):
            return outputdata
        # mc["outdata"]["light_orbitals.mkv"]["libx264"]["crf"][outputname] \
        #    [metric]. Dump mt2 as JSON
        return {
            k: {i: j for i, j in v.items() if outputname in j.values()}
            for k, v in outputdata.items()}

    @staticmethod
    def od_by_metric(outputdata, metric):
        if metric is None or not isinstance(metric, str):
            return outputdata

        return {k: {i: {m: {s: t
                            for s, t in n.items() if metric in t.keys()}
                        for m, n in j.items()}
                    for i, j in v.items()}
                for k, v in outputdata.items()}

    def basenames(self):
        return list(self.__mc["outputdata"].keys())

    def codecs(self):
        return self.__options.codecs()["videocodecs"]

    def paramsets(self):
        return list(self.__options.encoding_sets().keys())

    def by_file(self, filename):
        if filename is None or not isinstance(filename, str) \
                or not filename in self.basenames():
            return self.__mc["outputdata"]

        return {k: v for k, v in
                self.__mc["outputdata"].items() if filename in k}

    # video codecs for now
    def by_codec(self, codec):
        if codec is None or not isinstance(codec, str) \
                or not codec in self.codecs():
            return self.__mc["outputdata"]

        return {k: v for k, v in self.__mc["outputdata"].items()
                if codec in v.keys()}

    def by_paramset(self, paramset):
        if paramset is None or not isinstance(paramset, str) \
                or not paramset in self.paramsets():
            return self.__mc["outputdata"]

        # for k, v in self.__mc.outputdata.items():
        #     for i, j in v.items():
        #         if paramset in j.keys():
        #             pass
        return {
            k: {i: j for i, j in v.items() if paramset in j.keys()}
            for k, v in self.__mc["outputdata"].items()
        }

    def by_fqn_output(self, outputname):
        if outputname is None or not isinstance(outputname, str):
            return self.__mc["outputdata"]
        # for k, v in self.__mc.outputdata.items():
        #    for i, j im v.items():
            # paramset in j.keys()
            # paramset values in j.values() which are a dict
            # that contains the fqn output name, and as value the
            # metrics dict, with metrics name : actual dataframe
            # to match fqn output, check if name in j.values()
        # mc["outdata"]["light_orbitals.mkv"]["libx264"]["crf"][outputname] \
        #    [metric]
        return {
            k: {i: j for i, j in v.items() if outputname in j.values()}
            for k, v in self.__mc["outputdata"].items()
        }

    def by_metric(self, metric):
        if metric is None or not isinstance(metric, str):
            return self.__mc["outputdata"]

        # for k, v in outputdata.items():
        #    for i, j in v.items():
        #        for m, n in j.items():
        #            for s, t in n.items():
        #                print(f"t = {t.keys()}") for i, j in v.items()} for k
        return {k: {i: {m: {s: t
                            for s, t in n.items() if metric in t.keys()}
                        for m, n in j.items()}
                    for i, j in v.items()}
                for k, v in self.__mc["outputdata"].items()}

    @property
    def videoqtests(self):
        return self.__videoqt

    @videoqtests.setter
    def videoqtests(self, videoqt):
        if videoqt is not None and isinstance(videoqt, VideoQualityTests):
            self.__videoqt = videoqt

    @videoqtests.deleter
    def videoqtests(self):
        del self.__videoqt

    def populate_test_files(self, io_files_list = None):
        # now we have a dict where the keys are the original media, and the values
        # are a list of the compressed files, so we can run the tests
        if io_files_list is not None:
            self.__io_files_list = io_files_list
        else:
            self.__io_files_list = self.__encoder.qualify_output_files()






