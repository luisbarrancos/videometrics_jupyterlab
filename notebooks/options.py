#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 06:08:14 2021

@author: cgwork
"""


class Options:
    """A class for FFMPEG encoding options."""

    __verbosity = ["warning", "error", "panic"]
    # For AV1, libaom-av1 requires -strict -2 (experimental codec)
    # or use libsvtav1
    # __vcodecs = [
    #     "libx264", "libx265", "libvpx", "libvpx-vp9", "libaom-av1"]
    __vcodecs = [
        "libx264", "libx265", "libvpx", "libvpx-vp9", "libsvtav1"]
    __acodecs = ["copy", "aac", "mp3", "vorbis"]
    __containers = ["mp4", "mkv", "webm"]
    __chroma_sampling = ["yuv420p", "yuv422p", "yuv444p"]

    def __init__(self):
        # Regarding options, not all are supported accross codecs
        # ideally we would restrict this or make a mapping where possible
        #
        self.__common_options = {
            "c:v": "libx264",
            "f": "mp4",
            "coder": "cabac",
            # "trellis" : 2,
            # "b_strategy" : 2, # default 1=fast, 2=slower B-frame decision
            "color_range": "pc",
            "loglevel": "error",
            "export_side_data": "venc_params",
        }
        self.__encode_options = {
            "crf": 23,
            "preset": "veryfast",
            "tune": "film",
            "motion-est": "esa",
            "aq-mode": -1,
            "weightp": -1,
            "pix_fmt": "yuv420p",
        }
        self.__encoding_sets = {
            "crf": [18, 27, 36],
            "preset": ["veryfast", "medium"],
            "tune": ["film", "grain"],
            "motion-est": ["esa", "umh"],
            "aq-mode": [2, 3],
            "weightp": [0, 1, 2],
            "pix_fmt": self.__chroma_sampling,
        }
        self.__rate_control = {
            # All rates in kbit/s
            "singlepass": {
                "ratecontrol": {
                    "crf": {
                        "crf": self.__encoding_sets["crf"],
                    },
                    "cbr": {
                        "b:v": 1000,
                        "minrate": 1000,
                        "maxrate": 1000,
                        "bufsize": 2000,
                        "x264-params": {
                            "hal-hrd": "cbr",
                            "force-cfr": 1,
                        },
                    },
                },
            },
            "doublepass": {
                "ratecontrol": {
                    "capped_crf": {
                        "crf": self.__encoding_sets["crf"],
                        "b:v": 1000,
                        "minrate": 1000,
                        "maxrate": 1000,
                        "bufsize": 2000,
                        "x264-params": {
                            "hal-hrd": "cfr",
                            "force-cfr": 1,
                        },
                    }
                }
            },
        }

    def verbosity(self, level):
        """
        Set the FFMPEG encoding log level.

        Parameters
        ----------
        level : string
            One of "warning", "error", "panic", others ignored.

        Returns
        -------
        None.

        """
        if level in self.__verbosity:
            self.__common_options["loglevel"] = level

    def entropy_encoding(self, coder):
        """
        Set the choice of entropy encoding.

        Parameters
        ----------
        coder : string
            One of "cabac", "cavlc", "ac". CABAC is the default.

        Returns
        -------
        None.

        """
        if coder in ["cabac", "cavlc", "ac"]:
            self.__common_options["coder"] = coder

    def container(self, container):
        """
        Set the choice of container for the codec used. MP4, MKV, WEBM only.

        Parameters
        ----------
        container : string
            The container used, either MP4, MKV or WEBM, depending on codec.

        Returns
        -------
        None.

        """
        if container in self.__containers:
            self.__common_options["f"] = container

    def codec(self, vcodec=None, acodec=None):
        """
        Set the video and/or audio codecs fr compression.

        Parameters
        ----------
        vcodec : str, optional
            Choice of video codec. It can be one of libx264, libx265, libvpx
            for VP8, libvpx-vp9 for VP9, aom-av1 for AV1. The default is None.
        acodec : str, optional
            Choice of audio codec. It can be one of copy, mp3, aac, vorbis or
            opus. The default is None.

        Returns
        -------
        None.

        """
        if vcodec is not None and vcodec in self.__vcodecs:
            self.__common_options["c:v"] = vcodec

        if acodec is not None and acodec in self.__acodecs:
            self.__common_options["c:a"] = acodec

    def codecs(self):
        """
        Return dict with the list of video and audio codecs.

        Returns
        -------
        Dict[str, List[str]]
            List of codecs for the encoding sets processing.

        """
        return {"videocodecs": self.__vcodecs,
                "audiocodecs": self.__acodecs}

    def chroma_sampling(self, sampling):
        """
        Set the chroma sampling for the compression.

        Parameters
        ----------
        sampling : str
            String describing the chroma sampling for video compression.
            It can be one of "yuv420p", "yuv422p", "yuv444p"

        Returns
        -------
        None.

        """
        if sampling in self.__chroma_sampling:
            self.__encode_options["pix_fmt"] = sampling

    def common_options(self):
        """
        Return the common options used for compression.

        Returns
        -------
        dict
            Dictionary with common FFMPEG options for the analysis,
            encoding passes if any, and common amongst codecs.

        """
        return self.__common_options

    def encode_options(self):
        """
        Return the compression options that will be used.

        Returns
        -------
        dict
            Dictionary where keys are the compression methods that
            will be used, and the values the list containing the values
            to iterate over when compressing with such method.

        """
        return self.__encode_options

    def encoding_sets(self):
        """
        Return the test methods dictionary.

        Returns
        -------
        dict
            Dictionary of arrays, i.e, {"crf" : [23, 44]}.

        """
        return self.__encoding_sets

    def rate_control(self):
        """
        Return the rate control methods avaiiable.

        Returns
        -------
        dict
            Nested dictionary with rate control methods for the codec.

        """
        return self.__rate_control

    def insert_encoding_options(self, options):
        """
        Insert encoding options via dictionaries.

        Parameters
        ----------
        options : dict
            Dictionary containing extra encode specific options in the
            form key = compression name for ffmpeg, i.e, {"crf" : 23}

        Returns
        -------
        None.

        """
        if options is not None and isinstance(options, dict):
            for key, val in options:
                self.__encode_options[key] = val

    def insert_encoding_sets(self, encoding_sets, replace=False):
        """
        Insert encoding sets as dictionary of lists.

        Insert encoding sets iterables as a dictionary of lists, for
        example, if you want to encode with all the CRF options in a list
        containing [23, 28, 51] you would pass a dictionary with the following
        methods={"crf" : [23, 28, 51]}.

        Parameters
        ----------
        methods : dict, optional
            Dictionary of arrays with encoding methods. The default is None.

        Returns
        -------
        None.

        """
        if replace is True:
            self.__encoding_sets.clear()

        if encoding_sets is not None and isinstance(encoding_sets, dict):
            for key, val in encoding_sets.items():
                self.__encoding_sets[key] = val \
                    if isinstance(val, list) else list(val)
