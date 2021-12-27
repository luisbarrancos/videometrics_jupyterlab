#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 06:44:38 2021

@author: cgwork
"""

import copy as cp

import ffmpeg

#
# encode_video
# iterate_parameter
# iterate_methods
# iterate_videos


class Encoder:
    """Automated video encoding class through FFMPEG parameter sets."""

    def __init__(self, media, options):
        self.__media = media  # md.Media
        self.__options = options  # op.Options
        # op.Options has
        # common_options | encode_options | encoding_sets (iters)

    @staticmethod
    def encode_video(video_in, video_out, options):
        """
        Encode video with the FFMPEG options passed.

        Parameters
        ----------
        video_in : str
            Input video filename.
        video_out : str
            Output video filename.
        options : dict
            FFMPEG options in key:pair form.

        Returns
        -------
        None.

        """
        vin = ffmpeg.input(video_in)
        ffmpeg.output(vin, video_out, **options).overwrite_output().run()

    def encoding(self, video_in, video_out):
        """
        Encode video with the option sets configuration.

        Parameters
        ----------
        video_in : str
            Input video filename.
        video_out : str
            Output video filename.

        Returns
        -------
        None.

        """
        for key, values in self.__options.encoding_sets().items():
            encode_options = cp.deepcopy(self.__options.encode_options())
            # key = "crf", val = [18, 23, 31] for example

            for val in values:
                encode_options[key] = val
                options = {
                    **self.__options.common_options(),
                    **encode_options
                    }

                # TODO: build final output filename with encoding set arg val
                self.encode_video(video_in, video_out, options)

    def encode_videos(self):
        """
        Encode all the videos in the input media list iterating over options.

        Returns
        -------
        None.

        """
        for video_in, video_out in zip(
            self.__media.input_files(), self.__media.output_files()
        ):
            self.encoding(video_in, video_out)
