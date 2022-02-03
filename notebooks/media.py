#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 11:08:01 2021

@author: cgwork
"""
import os
from typing import Any, Dict, List, Optional, Union

import ffmpeg
from dotenv import dotenv_values


class Media:
    """Media interface for FFMPEG probe, containing related stream data."""

    def __init__(self) -> None:

        self.__config: Dict[Any, Any] = {}
        self.__info: Dict[Any, Any] = {}
        self.__config["original_dir"] = os.getenv("VIDEO_RESOURCES", None)
        self.__config["compressed_dir"] = os.getenv("VIDEO_COMPRESSED", None)

        if not any(self.__config.values()):
            dotfile = os.path.join(os.path.dirname(os.getcwd()), ".env")
            if os.path.isfile(dotfile):
                _tmp = dotenv_values(dotfile)
                self.__config["original_dir"] = _tmp["VIDEO_RESOURCES"]
                self.__config["compressed_dir"] = _tmp["VIDEO_COMPRESSED"]
            else:
                print(
                    "No VIDEO_RESOURCES nor VIDEO_COMPRESS environment"
                    "variables found defining the location of the original"
                    "uncompressed media, and the compressed media location"
                    ", neither .env file defining them."
                )

        self.__containers: List[str] = ["mp4", "mkv", "webm"]
        self.__input_dir: Union[str, os.PathLike,
                                None] = self.__config["original_dir"]
        self.__output_dir: Union[str, os.PathLike,
                                 None] = self.__config["compressed_dir"]

    def glob_media(self, containers: List[str] = None) -> None:
        """
        Glob all media of extension set in containers.

        Glob all media of extension set in containers under the directories
        defined by the VIDEO_RESOURCES environment variable or dotenv file.

        Parameters
        ----------
        containers : list, optional
            List of video containers, i.e, mkv, mp4. The default is None.

        Returns
        -------
        None.

        """
        _containers = containers if containers is not None else self.containers()

        self.__config["media_in"] = [
            os.path.join(self.input_dir(), x)
            for x in os.listdir(self.input_dir())
            if x.split(".")[1] in _containers
        ]
        self.__config["media_out"] = [
            os.path.join(self.output_dir(), x)
            for x in os.listdir(self.input_dir())
            if x.split(".")[1] in _containers
        ]

    def input_dir(self) -> Union[str, os.PathLike, None]:
        """
        Get the original source material directory.

        Returns
        -------
        str
            Path to the original source material directory.

        """
        return self.__input_dir

    def output_dir(self) -> Union[str, os.PathLike, None]:
        """
        Get the compressed material directory.

        Returns
        -------
        str
            Path to the compressed material directory.

        """
        return self.__output_dir

    def input_files(self) -> Union[List[str], None]:
        """
        Return a list of globbed files from the source material directory.

        Returns
        -------
        List[str]
            List of media files under the source material directory.

        """
        if "media_in" in self.__config:
            return self.__config["media_in"]
        return None

    def output_files(self) -> Union[List[str], None]:
        """
        Return a list with output base filenames for compression.

        Returns
        -------
        list
            A list with output base destination filenames for compression.

        """
        if "media_out" in self.__config:
            return self.__config["media_out"]
        return None

    def containers(self) -> List[str]:
        """
        Return the list of containers to glob in the input media directory.

        Returns
        -------
        list
            Containers to glob in the input media directory.

        """
        return self.__containers

    def config(self) -> Dict[str, Union[str, List[str]]]:
        """
        Return the configuration dictionary for input, compressed material.

        Returns
        -------
        dict
            The configuration dictionary containing the source/original videos
            directory, the destination compressed directory, and the globbed
            list of files found under the source directory as well as the
            prepared base filename destination files.

        """
        return self.__config

    def set_input_dir(self, original_dir: str) -> None:
        """
        Set the directory containing the original source videos
        overriding the environment VIDEO_RESOURCES.

        Parameters
        ----------
        original_dir : str
            The full path to the original media directory.

        Returns
        -------
        None.

        """
        self.__config["original_dir"] = original_dir

    def set_output_dir(self, compressed_dir: str) -> None:
        """
        Set the directory containing the compressed videos
        overriding the environment VIDEO_COMPRESSED.

        Parameters
        ----------
        compressed_dir : str
            The full path to the compressed media directory.

        Returns
        -------
        None.

        """
        self.__config["compressed_dir"] = compressed_dir

    def info(self, media: Optional[str] = None) -> Dict[str, Any]:
        """
        Return the media probe information in a dictionary form.

        When invoked without arguments it returns a dictionary containing as
        keys the filenames from the media list, and as values, dictionaries
        with the ffprobe media info.
        When called with a filename as argument, it returns that media file
        ffprobe media information instead.


        Parameters
        ----------
        media : str, optional
            A individual media file to get the info from. The default is None.

        Returns
        -------
        dict
            The FFprobe media information for each media file in the list
            of media files, in dictionary form, with key being the full
            filename and value being the FFProbe information.
            When called with a filename argument, it returns instead a single
            media file ffprobe information.

        """
        media_data = self.probe_all()
        if media is not None and isinstance(media, str) and media in media_data:
            return media_data[media]

        return self.probe_all()

    @staticmethod
    def probe(video: str) -> Dict[str, str]:
        """
        Return the video stream info via FFMPEG ffprobe.

        Parameters
        ----------
        video : str
            Path and filename to query information from.

        Returns
        -------
        video_info : dict
            Dictionary of metadata, tags, found in the media file via FFprobe.

        """
        probe = ffmpeg.probe(video)
        video_info = next(
            stream for stream in probe["streams"] if stream["codec_type"] == "video"
        )
        return video_info

    def probe_all(self) -> Dict[str, Any]:
        """
        Video metadata/tags from every globbed media file in the source dir.

        Returns
        -------
        dict
            Dictionary with source material filename as key, and as value the
            set of metadata/tags found by FFprobe.

        """
        for video in self.input_files():
            self.__info[str(video)] = self.probe(video)
        return self.__info

    def width(self, video: str) -> int:
        """
        Return the width of the input video.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        int
            Video width.

        """
        return int(self.probe(video)["width"])

    def height(self, video: str) -> int:
        """
        Return the height of the input video.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        int
            Video height.

        """
        return int(self.probe(video)["height"])

    def framerate(self, video: str) -> int:
        """
        Return the frame rate (not average) of the input video file.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        int
            Input video framerate, i.e, 25fps for PAL.

        """
        return int(self.probe(video)["r_frame_rate"].split("/")[0])

    # according to docs, return type of Optional[type] is Union[typel, None]
    # therefore nullable object, but we can use Union (explicit) or | (or)
    # but the OR operator is only available in python 3.10+
    def duration(self, video: str) -> Union[List[int], None]:
        """
        Get the input video duration in hh:mm:ss:msecs format.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        list
            List containing the video duration in hours, minutes, seconds and
            milliseconds.

        """
        info = self.probe(video)["tags"]

        if "DURATION" not in info.keys():
            print(f"No DURATION tag found in {video} probe.")
            return None

        hours, minutes, seconds = info["DURATION"].split(":")
        seconds, milliseconds = seconds.split(",")
        hours, minutes, seconds, milliseconds = map(
            lambda x: int(x) if len(x) < 3 else round(int(x) * 1e-6),
            [hours, minutes, seconds, milliseconds],
        )
        return [hours, minutes, seconds, milliseconds]

    def number_of_seconds(self, video: str) -> int:
        """
        Get the duration of the input video in seconds.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        int
            Total duration of the input video in seconds.

        """
        hours, minutes, seconds, milliseconds = self.duration(video)
        return round(hours * 3600 + minutes * 60 + seconds + milliseconds)

    def number_of_frames(self, video: str) -> int:
        """
        Get the duration of the input video in frames, depends on frame rate.

        Parameters
        ----------
        video : str
            Input video filename.

        Returns
        -------
        int
            Total duration of the input video in frames, depends on frame rate.

        """
        if "nb_frames" in self.probe(video):
            return self.probe(video)["nb_frames"]

        frame_rate = self.framerate(video)
        time_base = int(self.probe(video)["time_base"].split("/")[1])

        hours, mins, secs, milliseconds = self.duration(video)
        remaining_frames = int((milliseconds / float(time_base)) * frame_rate)
        frames = frame_rate * (3600 * hours + 60 *
                               mins + secs) + remaining_frames

        return frames

    @staticmethod
    def __video_bitrate(total_bitrate: int, audio_bitrate: Optional[int] = 0) -> int:
        """
        Compute the video bitrate according to total and audio bitrate.

        Parameters
        ----------
        total_bitrate : int
            Total available bitrate for the AV stream.
        audio_bitrate : int, optional
            Available bitrate for the audio stream. The default is 0.

        Returns
        -------
        int
            Available bitrate for the video stream.

        """
        return total_bitrate - audio_bitrate

    @staticmethod
    def __audio_bitrate(video: str, audio_bitrate: Optional[int] = 0) -> int:
        """
        Return the audio bitrate found in the audio stream, or overriden.

        Parameters
        ----------
        video : str
            Input video filename.
        audio_bitrate : int, optional
            Available bitrate for the audio stream. The default is 0.

        Returns
        -------
        int
            Audio bitrate from existing AV stream, or manually allocated.

        """
        if audio_bitrate != 0:
            return audio_bitrate

        if ffmpeg.probe(video, select_streams="a")["streams"]:
            bitrate = float(
                next(
                    (
                        s
                        for s in ffmpeg.probe(video)["streams"]
                        if s["codec_type"] == "audio"
                    ),
                    None,
                )["bit_rate"]
            )
            return bitrate
        return 0

    @staticmethod
    def __total_bitrate(target_size_mib: int, duration_secs: int) -> int:
        """
        Total bitrate to use for given size in MiB and duration in seconds.

        Parameters
        ----------
        target_size_mib : int
            Target file size in MiB, i.e, 1MiB = 1024KiB.
        duration_secs : int
            Duration of the media stream.

        Returns
        -------
        int
            Total bitrate for a given target size and duration.

        """
        # convert to KiB, then to Kbit/s
        return int(target_size_mib * 1024 * 8 / float(duration_secs))

    def bitrates_for_size(self, video: str, target_size_mib: int) -> Dict[str, int]:
        """
        Total, audio, video bitrates for given media and desired file size.

        Parameters
        ----------
        video : str
            Input media file.
        target_size_mib : int
            Desired media file size in MiB.

        Returns
        -------
        dict
            Dictionary containing the keys "total_bitrate", "video_bitrate"
            and "audio_bitrate" with their computed values in function of
            the media stream duration and desired final file size.

        """
        duration_secs = self.number_of_seconds(video)
        total_bitrate = self.__total_bitrate(target_size_mib, duration_secs)

        audio_bitrate = self.__audio_bitrate(video)
        video_bitrate = self.__video_bitrate(
            total_bitrate, audio_bitrate=audio_bitrate)

        return {
            "total_bitrate": total_bitrate,
            "video_bitrate": video_bitrate,
            "audio_bitrate": audio_bitrate,
        }
