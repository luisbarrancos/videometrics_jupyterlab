#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 18:22:45 2022

@author: cgwork
"""

# marshmallow schemas
# marshmallow-dataclass (mm schemas from dataclasses)
# marshmallow-dataframes (same for pandas dataframes)

# https://github.com/Fatal1ty/mashumaro

#import json

#from marshmallow import Schema
#from marshmallow_dataclass import dataclass
#from dataclasses import field, asdict

import os
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Dict, List, Optional, Type, Union

from mashumaro import DataClassJSONMixin

# define a type hint for JSON files, but Pandas DataFrames must be
# converted. This however is a general data structure, not the file itself
# NOTE: not so sure about this
JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]

#from media import Media
#from options import Options

# VQ metrics are created from FFMPEG as dict, we do convert later though
# and this is something to be processed **LATER**
# we want NOW to have a structure to save and load from json
# what we convert later to a dataframe and process is for another step

#from pandas import DataFrame


"""
# NOTE: originally VQ metrics is a dict, which makes things easier to
# move back into a pandas dataframe

container =
{
    inputdir:
    [
        orig1 : mediainfo,
        orig2 : mediainfo,
        orig3 : mediainfo,
        ...
    ],

    outputdir:
    [
        output_basename_orig1:
        {
            codec_A:
            {
                param_set_1:
                {
                    ouput_file_fqn.ext:
                    {
                        vqa_metrics:
                        {
                            SSIM : dataframe,
                            PSNR : dataframe,
                            MSE  : dataframe,
                            VIF  : dataframe,
                            VMAF : dataframe
                        },
                    },
                    output_file2_fq.ext: { ... },
                    output_file3_fq.ext: { ... },
                    ...
                },
                param_set_2:
                {
                    output_file_fqn.ext: { ... }
                },
                ...
            },
            codec_B: {...}
            ...
        },
        output_basename_orig2: {...}
        ...
    ]
}

@dataclass
class VideoQuality:
    _metrics: Dict[str, DataFrame] = field(default_factory=dict)

    @property
    def metrics(self) -> Dict[str, DataFrame]:
        return self._metrics

    @metrics.setter
    def metrics(self, key: str, dataframe: DataFrame) -> None:
        self._metrics[key] = dataframe

    @metrics.deleter
    def metrics(self) -> None:
        del self._metrics
"""


@dataclass
class VideoQuality(DataClassJSONMixin):
    _metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def metrics(self) -> Dict[str, Dict[str, Any]]:
        return self._metrics

    @metrics.setter
    def metrics(self, data: Dict[str, Dict[str, Any]]) -> None:
        self._metrics = data

    @metrics.deleter
    def metrics(self) -> None:
        del self._metrics


# VideoQuality = dict of dataframes, to/from json as well, save with
# same FQN output with extension changed
@dataclass
class QualifiedOutput(DataClassJSONMixin):
    _fqn_output: Dict[Union[str, PathLike],
                      VideoQuality] = field(default_factory=dict)

    @property
    def entries(self) -> Dict[Union[str, PathLike], VideoQuality]:
        return self._fqn_output

    @entries.setter
    def entries(self, outfile: Union[str, PathLike], videoqual: VideoQuality) -> None:
        self._fqn_output[outfile] = videoqual

    @entries.deleter
    def entries(self) -> None:
        del self._fqn_output


@dataclass
class Parameters(DataClassJSONMixin):
    _param_set: Dict[str, QualifiedOutput] = field(default_factory=dict)

    @property
    def sets(self) -> Dict[str, QualifiedOutput]:
        return self._param_set

    @sets.setter
    def sets(self, param: str, fqo: QualifiedOutput) -> None:
        self._param_set[param] = fqo

    @sets.deleter
    def sets(self) -> None:
        del self._param_set


@dataclass
class Codec(DataClassJSONMixin):
    _vcodec: Dict[str, Parameters] = field(default_factory=dict)
    # _acodec, copy

    @property
    def video(self) -> Dict[str, Parameters]:
        return self._vcodec

    @video.setter
    def video(self, vcodec: str, params: Parameters) -> None:
        self._vcodec[vcodec] = params

    @video.deleter
    def video(self) -> None:
        del self._vcodec


@dataclass
class MediaInfo(DataClassJSONMixin):
    _mediainfo: Dict[Union[str, PathLike],
                     Dict[str, Any]] = field(default_factory=dict)

    @property
    def mediainfo(self) -> Dict[Union[str, PathLike], Dict[str, Any]]:
        return self._mediainfo

    @mediainfo.setter
    def mediainfo(self, input_info: Dict[Union[str, PathLike], Dict[str, Any]]) -> None:
        self._mediainfo = input_info

    @mediainfo.deleter
    def mediainfo(self) -> None:
        del self._mediainfo


@dataclass
class OutputBasename(DataClassJSONMixin):
    _output_basename: Dict[str, Codec] = field(default_factory=dict)

    @property
    def output_basename(self) -> Dict[str, Codec]:
        return self._output_basename

    @output_basename.setter
    def output_basename(self, out_name: str, cdc: Codec) -> None:
        self._output_basename[out_name] = cdc

    @output_basename.deleter
    def output_basename(self) -> None:
        del self._output_basename


@dataclass
class MediaContainer(DataClassJSONMixin):
    """Automated video encoding class through FFMPEG parameter sets."""
    # dir on which to glob files
    _inputdir: Union[str, PathLike] = field(default_factory=str)
    # probe all , for all globbed files under inputdir, this is a media info obj
    _inputdata: MediaInfo = field(default_factory=MediaInfo)
    # same for output directory
    _outputdir: Union[str, PathLike] = field(default_factory=str)
    # and the storage for the dictionaries, dataframes
    _outputdata: List[OutputBasename] = field(default_factory=list)

    @property
    def inputdir(self) -> Union[str, PathLike]:
        return self._inputdir

    @inputdir.setter
    def inputdir(self, indir: Union[str, PathLike]) -> None:
        self._inputdir = indir

    @inputdir.deleter
    def inputdir(self) -> None:
        del self._inputdir

    @property
    def outputdir(self) -> Union[str, PathLike]:
        return self._outputdir

    @outputdir.setter
    def outputdir(self, outdir: Union[str, PathLike]) -> None:
        self._outputdir = outdir

    @outputdir.deleter
    def outputdir(self) -> None:
        del self._outputdir

    @property
    def inputdata(self) -> MediaInfo:
        return self._inputdata

    @inputdata.setter
    def inputdata(self, minfo: MediaInfo) -> None:
        self._inputdata = minfo

    @inputdata.deleter
    def inputdata(self) -> None:
        del self._inputdata

    @property
    def outputdata(self) -> List[OutputBasename]:
        return self._outputdata

    @outputdata.setter
    def outputdata(self, outdata: List[OutputBasename]) -> None:
        self._outputdata = outdata

    @outputdata.deleter
    def outputdata(self) -> None:
        del self._outputdata


# Serialization/deserialization to JSON via dataclasses asdict and
# make_dataclasses, however mashumiro already extends the dataclass with
# to_json, from_json methods.
# The only interesting tidbit left is:
# marshmallow : https://github.com/marshmallow-code/marshmallow

def save_mc(mc_inst: MediaContainer,
            filename: Union[str, PathLike],
            overwrite: Optional[bool] = True) -> None:
    if overwrite is False and os.path.exists(filename):
        raise FileExistsError

    # mashumaro serialization
    if isinstance(mc_inst, MediaContainer):
        data: str = str(mc_inst.to_json())

        with open(filename, "w") as jsonfile:
            jsonfile.write(data)


def load_mc(filename: Union[str, PathLike]) -> MediaContainer:
    if not os.path.exists(filename):
        raise IOError

    jsondata: str = ""
    with open(filename, "r") as jsonfile:
        jsondata = jsonfile.read()

    media: MediaContainer = MediaContainer()
    media.from_json(jsondata)
    return media


# TODO: Add unit tests

#from media import Media

#md = Media()
# md.glob_media()
# md.input_files()
#mc = MediaContainer(md.input_dir(), md.probe_all())

#json_foo = json.dumps(asdict(mc))
# print(type(json_foo))
# print(json_foo)

#test = mc.to_json()


# test
# def build_container():
#    vq = Video
