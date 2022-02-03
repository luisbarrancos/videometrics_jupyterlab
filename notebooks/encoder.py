#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 06:44:38 2021

@author: cgwork
"""

import copy as cp
from typing import Any, Dict, List, Optional, Union

import ffmpeg
from media import Media
from options import Options


class Encoder:
    """Automated video encoding class through FFMPEG parameter sets."""

    def __init__(self, media: Union[Media, None], options: Union[Options, None]) -> None:
        self.__media: Media = media  # md.Media
        self.__options: Options = options  # op.Options
        # output basename + parameters
        self.__full_test_filenames: Dict[str, Any] = {}
        # op.Options has
        # common_options | encode_options | encoding_sets (iters)

    def set_media(self, media: Union[Media, None]) -> None:
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

    def set_options(self, options: Union[Options, None]) -> None:
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

    def media(self) -> Media:
        """
        Getter for media object instance.

        Returns
        -------
        Media
            Media object instance with media input, output lists.

        """
        return self.__media

    def options(self) -> Options:
        """
        Geetter for options object instance.

        Returns
        -------
        Options
            Options object instance with options input, output lists.

        """
        return self.__options

    def full_test_filenames(self) -> List[str]:
        """
        Return the fully assembled VQA output test filenames.

        Returns
        -------
        list
            Return a list of strings with full formatted test filenames with
            appended parameters in the form <output_base_filename>__+
            <param>__<value>__(...).<ext>.
            Example, foobar__crf_23__preset_high__... .mp4
        """
        return self.__full_test_filenames

    @staticmethod
    def encode_video(
            video_in: str,
            video_out: str,
            options: Options,
            debug: Optional[bool] = False) -> None:
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

    def encoding(self,
                 video_in: str,
                 video_out: str,
                 debug: Optional[bool] = False) -> List[str]:
        """
        Encode video with the option sets configuration.

        Parameters
        ----------
        video_in : str
            Input video filename.
        video_out : str
            Output video filename.
        debug: bool, optional
            Skip encoding and print the full test filenames.

        Returns
        -------
        full_test_filenames : list
            Return a list of strings with full formatted test filenames with
            appended parameters in the form <output_base_filename>__+
            <param>__<value>__(...).<ext>.
            Example, foobar_-_crf_23__preset_high__... .mp4

        """
        # make it nested dict then
        #        full_test_filenames[video_in][fname] = {
        #            "options" : options,
        #            "dfmetrics" : {}
        #            }
        full_test_filenames = {video_in: []}

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
                fname = f"{fname}_-_{fname_suffix}.{ext}"
                # for each video input, store the variation sets of the
                # compressed test videos
                full_test_filenames[video_in].append(fname)

                options = {
                    **self.__options.common_options(),
                    **encode_options
                }

                if debug is True:
                    print(f"input {video_in}, output = {fname}")
                else:
                    self.encode_video(video_in, fname, options)

        self.__full_test_filenames = cp.deepcopy(full_test_filenames)

    def encode_videos(self, debug: Optional[bool] = False) -> None:
        """
        Encode all the input list videos with the options set.

        Returns
        -------
        None.

        """
        # foreach video in, output file in the zipped lists
        for video_in, video_out in zip(
            self.__media.input_files(), self.__media.output_files()
        ):
            self.encoding(video_in, video_out, debug=debug)
