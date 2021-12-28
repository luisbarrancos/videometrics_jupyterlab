#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 06:44:38 2021

@author: cgwork
"""

import copy as cp

import ffmpeg

# import media as md
# import options as op


class Encoder:
    """Automated video encoding class through FFMPEG parameter sets."""

    def __init__(self, media, options):
        self.__media = media  # md.Media
        self.__options = options  # op.Options
        # op.Options has
        # common_options | encode_options | encoding_sets (iters)

    def set_media(self, media):
        """
        Set the input media and output media object.

        Parameters
        ----------
        media : class
            Media object instance, containing the input, output media list.

        Returns
        -------
        None.

        """
        if media is not None and isinstance(media, media.Media):
            self.__media = media

    def set_options(self, options):
        """
        Set the options for encoding.

        Parameters
        ----------
        options : class
            Options object instance, containing the common, encoding, sets.

        Returns
        -------
        None.

        """
        if options is not None and isinstance(options, options.Options):
            self.__options = options

    def media(self):
        """
        Getter for media object instance.

        Returns
        -------
        Media
            Media object instance with media input, output lists.

        """
        return self.__media

    def options(self):
        """
        Geetter for options object instance.

        Returns
        -------
        Options
            Options object instance with options input, output lists.

        """
        return self.__options

    @staticmethod
    def encode_video(video_in, video_out, options, debug=False):
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
        debug : bool
            When true, skips encoding and dump the I/O media paths instead.

        Returns
        -------
        None.

        """
        if debug is True:
            print(f"in = {video_in}, out = {video_out}, opt = {options}")

        else:
            vin = ffmpeg.input(video_in)
            ffmpeg.output(
                vin,
                video_out,
                **options,
                ).overwrite_output().run()

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

                fname_suffix = "__".join(
                    map(
                        lambda x, y: x + "_" + str(y),
                        encode_options.keys(),
                        encode_options.values(),
                    )
                )

                fname, ext = video_out.split(".")
                fname = f"{fname}_{fname_suffix}.{ext}"
                options = {
                    **self.__options.common_options(),
                    **encode_options
                    }

                # print(f"input {video_in}, output = {fname}")
                self.encode_video(video_in, fname, options)

    def encode_videos(self):
        """
        Encode all the input list videos with the options set.

        Returns
        -------
        None.

        """
        for video_in, video_out in zip(
            self.__media.input_files(), self.__media.output_files()
        ):
            self.encoding(video_in, video_out)
