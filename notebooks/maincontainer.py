#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 08:49:02 2022

@author: cgwork
"""

from dataclasses import dataclass, field

from os import PathLike
from typing import Any, ClassVar, Dict, List, Tuple, Union, TypedDict
from typing import IO, BinaryIO, TextIO

"""

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









"""


@dataclass(unsafe_hash=True)
class SourceMedia:
    _input_dir: Union[str, PathLike, None] = field(default_factory = str)
    _files: List[Union[str, PathLike, BinaryIO, None]] = field(default_factory = list)

    @property
    def inputdir(self) -> Union[str, PathLike, None]:
        return self._input_dir

    @inputdir.setter
    def inputdir(self, inputdir : Union[str, PathLike, None]) -> None:
        self._input_dir = inputdir

    @property
    def files(self) -> List[Union[str, PathLike, BinaryIO, None]]:
        return self._files

    @files.setter
    def files(self, files : List[Union[str, PathLike, BinaryIO, None]]) -> None:
        self._files = files

