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
        self.__full_test_filenames = {}  # output basename + parameters
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
        Getter for options object instance.

        Returns
        -------
        Options
            Options object instance with options input, output lists.

        """
        return self.__options

    def full_test_filenames(self):
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

    def encoding(self, video_in, video_out, debug=False):
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


    def encode_videos(self, debug=False):
        """
        Encode all the input list videos with the options set.

        Returns
        -------
        None.

        """
        for video_in, video_out in zip(
            self.__media.input_files(), self.__media.output_files()
        ):
            self.encoding(video_in, video_out, debug=debug)


    def qualify_output_files(self):
        """
        Build fully qualified output file names with the parameter sets.

        Build a complete filename from the output base name, with the
        parameter set variations appended, i.e, basename_crf_23_... .ext

        Returns
        -------
        dict
            Dictionary where the key is the input media filename, and the
            values is a list of the parameter set variations fully qualified
            output filenames.

        """

        if self.__media.input_files() is not None and \
                self.__media.output_files() is not None:

            full_test_filenames = {}

            for video_in, video_out in zip(
                    self.__media.input_files(), self.__media.output_files()):

                full_test_filenames[video_in] = []

                for key, values in self.__options.encoding_sets().items():
                    encode_options = cp.deepcopy(
                        self.__options.encode_options())
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
            return full_test_filenames
        return None

    def fqn(self, basename):
        full_test_filenames = []

        for key, values in self.__options.encoding_sets().items():
            encode_options = cp.deepcopy(
                self.__options.encode_options())
            # key = "crf", val = [18, 23, 31] for example
            paramlist = []

            for val in values:
                encode_options[key] = val

                fname_suffix = "__".join(
                    map(
                        lambda x, y: x + "_" + str(y),
                        encode_options.keys(),
                        encode_options.values(),
                    )
                )

                fname, ext = basename.split(".")
                fname = f"{fname}_-_{fname_suffix}.{ext}"
                # for each video input, store the variation sets of the
                # compressed test videos
                #full_test_filenames.append(fname)
                paramlist.append(fname)

            full_test_filenames.append(paramlist)

        return full_test_filenames

    def build_fname(self, key, values, basename):
        enc = cp.deepcopy(self.__options.encode_options())
        paramlist = []
        for val in values:
            enc[key] = val
            fname_suffix = "__".join(
                map(lambda x, y: x + "_" + str(y),
                    enc.keys(),
                    enc.values(),
                    )
                )
            fname, ext = basename.split(".")
            fname = f"{fname}_-_{fname_suffix}.{ext}"
            paramlist.append(fname)
        return paramlist

    def build_fname_and_metric(self, key, values, basename):
        enc = cp.deepcopy(self.__options.encode_options())
        paramlist = []
        for val in values:
            enc[key] = val
            fname_suffix = "__".join(
                map(lambda x, y: x + "_" + str(y),
                    enc.keys(),
                    enc.values(),
                    )
                )
            fname, ext = basename.split(".")
            fname = f"{fname}_-_{fname_suffix}.{ext}"
            # fname : {"metricname" : metricdata_dict}
            paramlist.append({fname : {{}}})
        return paramlist
