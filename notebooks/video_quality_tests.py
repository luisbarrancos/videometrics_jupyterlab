#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 00:56:07 2021

@author: cgwork
"""


import json

import pandas as pd
from ffmpeg_quality_metrics import FfmpegQualityMetrics as ffqm

class VideoQualityTests:
    """ Video quality tests and auxiliary methods. """

    def __init__(self, io_files_list=None):
        self.__metrics = ["ssim", "psnr", "vmaf", "vif"]
        # dict( original : out_basename_params_encoding)
        self.__io_files_list = io_files_list

    @property
    def io_files_list(self):
        return self.__io_files_list

    @io_files_list.setter
    def io_files_list(self, fnames):
        self.__io_files_list = fnames

    @io_files_list.deleter
    def io_files_list(self):
        del self.__io_files_list

    @staticmethod
    def __moving_averages(df, metric, mean_period):

        dfn = df.copy(deep=True)
        sma = f"_sma{mean_period}"

        if metric == "psnr":
            dfn[f"psnr_y{sma}"] = (
                dfn["psnr_y"]
                .rolling(
                    window=mean_period, min_periods=mean_period)
                .mean()
            )
            dfn[f"mse_y{sma}"] = (
                dfn["mse_y"].rolling(
                    window=mean_period, min_periods=mean_period).mean()
            )
        elif metric == "ssim":
            dfn[f"psnr_y{sma}"] = (
                dfn["ssim_y"]
                .rolling(
                    window=mean_period, min_periods=mean_period)
                .mean()
            )
        elif metric == "vmaf":
            dfn[f"vmaf{sma}"] = (
                dfn["vmaf"].rolling(
                    window=mean_period, min_periods=mean_period).mean()
            )
            dfn[f"ms_ssim{sma}"] = (
                dfn["ms_ssim"]
                .rolling(
                    window=mean_period, min_periods=mean_period)
                .mean()
            )
            dfn[f"ssim{sma}"] = (
                dfn["ssim"].rolling(
                    window=mean_period, min_periods=mean_period).mean()
            )
            dfn[f"psnr{sma}"] = (
                dfn["psnr"].rolling(
                    window=mean_period, min_periods=mean_period).mean()
            )
        else:
            pass  # no moving averages for VIF

        return dfn

    @staticmethod
    def __get_dataframe(metric_data, metric):
        if metric in metric_data.keys():
            return pd.DataFrame.from_dict(metric_data[metric])

        print(f"No metric: {metric} found on metric data dict.")
        return None

    def get_metrics(self):
        """
        Get the list of video quality metrics used for the tests.

        Returns
        -------
        list
            List of metrics used for the tests.

        """
        return self.__metrics

    def set_metrics(self, metrics: list):
        """
        Set the list of metrics used for the tests.

        Parameters
        ----------
        metrics : list
            List of metrics for the tests. The default is SSIM, PSNR, VMAF.

        Returns
        -------
        None

        """
        if metrics is not None:
            self.__metrics = metrics if \
                isinstance(metrics, list) else list(metrics)

    @staticmethod
    def save_json(metrics_data, json_filename):
        """
        Save metrics test data as JSON file.

        Parameters
        ----------
        metrics_data : dict
            Metrics data, dictionary with key metric name and data results.
        json_filename : str
            Filename for the JSON data.

        Returns
        -------
        None

        """
        metrics_json = json.dumps(metrics_data, indent=4)

        with open(json_filename, "wt", encoding="utf8") as file:
            file.write(metrics_json)

    @staticmethod
    def load_json(filename):
        """
        Load JSON metrics test results.

        Parameters
        ----------
        filename : str
            JSON filename with metrics data.

        Returns
        -------
        dict
            Test results with key metric, and value the results for each frame.

        """
        with open(filename, "rt", encoding="utf8") as file:
            return json.load(file)
        return None

    @staticmethod
    def run_metrics(video_in,
                    video_out,
                    metrics, progress=False, vmaf_options=None):
        """
        Run the FFMPEG metrics on the original and distorted media.

        Parameters
        ----------
        video_in : str
            Original media.
        video_out : str
            Distorted media.
        metrics : list
            Metrics for the tests, defaults to SSIM, PSNR, VMAF, VIF.
        progress : bool, optional
            Toggles progress indication on or off. The default is False.
        vmaf_options : dict, optional
            Dictionary with key "model_path" with the model for the VMAF
            model data used. The default is None.

        Returns
        -------
        dict
            DESCRIPTION.

        """

        _ffqm = ffqm(video_in, video_out, progress=progress)

        if vmaf_options is not None and isinstance(vmaf_options, dict):
            metrics_data = _ffqm.calc(metrics, vmaf_options=vmaf_options)
        else:
            metrics_data = _ffqm.calc(metrics)

        return metrics_data

    def run_tests(self,
                  metrics, progress=False, vmaf_options=None):
        """
        Run the metric tests for the entire media in the lists.

        Parameters
        ----------
        metrics : list
            Metrics used, defaults to SSIM, PSNR, VMAF, VIF.
        progress : bool, optional
            Toggles progress indication on or off. The default is False.
        vmaf_options : dict, optional
            Dictionary with key "model_path" to the VMAF model path.
            The default is None.

        Returns
        -------
        None

        """
        if self.__io_files_list is None:
            raise ValueError

        for original, compressed_files in self.__io_files_list.items():
            for compressed_file in compressed_files:
                metrics_data = self.run_metrics(
                    original,
                    compressed_file,
                    metrics,
                    progress=progress,
                    vmaf_options=vmaf_options,
                )
                data = {
                    "original_media": original,
                    "compressed_media": compressed_file,
                    "vq_metrics": metrics,
                    "metrics_data": metrics_data,
                }
                json_filename = compressed_file.split(".")[0] + ".json"
                self.save_json(data, json_filename)

    # get the dataframes for the metrics of an individual file
    def get_dataframes(self,
                       metric_data,
                       moving_averages=False,
                       mean_period=50,
                       metrics=None):
        """
        Get Pandas DataFrames for the metrics data.

        Parameters
        ----------
        metric_data : dict
            The FFMPEG Metrics test data dictionary.
        moving_averages : bool, optional
            Toggles smoothing the data with simple moving average.
            The default is False.
        mean_period : int, optional
            Moving average window. The default is 50.
        metrics : list, optional
            List of metrics for the test data. The default is None.

        Returns
        -------
        dict
            Dictionary with key, the metric name, and with values, the Pandas
            DataFrames containing all the test data already cleaned.

        """
        dfs = {}
        vq_metrics = self.get_metrics() if metrics is not None else metrics

        for metric in vq_metrics:
            df = self.__get_dataframe(metric_data, metric)  # from dict

            if df is not None:
                df.rename(columns={"n": "frame"}, inplace=True)
                df.set_index("frame", inplace=True)

                if moving_averages is True:  # now do SMA on dataframes
                    df = self.__moving_averages(df, metric, mean_period)

            dfs[metric] = df

        return dfs  # dict {"ssim" : df_ssim_metric, ...}

    def get_all_data(self):
        """
        Load the precomputed JSON metrics data for all I/O media.

        Returns
        -------
        data : list
            Return an array of dictionaries in the form:
            [
                {
                    "original" : "/path/to/original_media1.mkv,
                    "compressed_files" :
                        {
                            "path/to/foo_crf_23_preset.mp4" : [df...],
                            "path/to/bar_crf_42_preset.mp4" : [df...],
                        }
                },
            ]
            for each original frame.
        """
        data = []
        for original, compressed_files in self.__io_files_list.items():

            io_media = {"original": original, "compressed_files": {}}

            for compressed_file in compressed_files:
                json_filename = compressed_file.split(".")[0] + ".json"
                json_data = self.load_json(json_filename)

                # array of pandas dataframes foreach metric in vq_metrics
                dfs = self.get_dataframes(
                    json_data["metrics_data"],
                    moving_averages=True,
                    mean_period=50,  # 2x 25fps assumed
                    metrics=json_data["vq_metrics"],
                )
                io_media["compressed_files"][compressed_file] = dfs
            data.append(io_media)

        return data
