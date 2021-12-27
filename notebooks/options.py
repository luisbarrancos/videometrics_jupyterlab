#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 06:08:14 2021

@author: cgwork
"""


class Options:
    """
    A class for FFMPEG encoding options

    """

    __verbosity = ["warning", "error", "panic"]
    __vcodecs = ["libx264", "libx265", "libvpx", "libvpx-vp9", "libaom-av1"]
    __acodecs = ["copy", "aac", "mp3", "vorbis"]
    __containers = ["mp4", "mkv", "webm"]
    __chroma_sampling = ["yuv420p", "yuv422p", "yuv444p"]

    def __init__(self):
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
        self.__options = {
            "crf": [18, 23, 27, 36],
            "preset": ["veryfast", "medium", "slower"],
            "tune": ["film", "animation", "grain"],
            "memethod": ["exa", "umh"],
        }

    def verbosity(self, level):
        """
        Set the FFMPEG encoding log level

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
        Set the choice of entropy encoding

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
        Sets the video and/or audio codecs fr compression.

        Parameters
        ----------
        vcodec : str, optional
            Choice of video codec. It can be one of libx264, libx265, libvpx for
            VP8, libvpx-vp9 for VP9, aom-av1 for AV1. The default is None.
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

    def chroma_sampling(self, sampling):
        """
        Set the chroma sampling for the compression

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
            self.__options["pix_fmt"] = sampling

    def compression_options(self):
        """
        Returns the compression options that will be used.

        Returns
        -------
        dict
            Dictionary where keys are the compression methods that
            will be used, and the values the list containing the values
            to iterate over when compressing with such method.

        """
        return self.__options

    def common_options(self):
        """
        Returns the common options used for compression

        Returns
        -------
        dict
            Dictionary with common FFMPEG options for the analysis,
            encoding passes if any, and common amongst codecs.

        """
        return self.__common_options

    def insert_options(self, options=None):
        """
        Insert compression options via dictionaries.

        Parameters
        ----------
        options : dict, optional
            Dictionary containing extra encode specific options in the
            form key = compression name for ffmpeg, and value is a list
            containing the values this option will iterate over.
            The default is None.

        Returns
        -------
        None.

        """
        if options is not None and isinstance(options, dict):
            for key, val in options:
                self.__options[key] = val if isinstance(val, list) else list(val)
