#!/usr/bin/env python3

"""Module containing the HelParCorrelation class and the command line interface."""
import argparse
from pathlib import Path

import pandas as pd
import numpy as np

from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_dna.dna.loader import load_data


class HelParCorrelation():
    """
    | biobb_dna HelParCorrelation
    |

    Args:
        input_filename_shift (str): Path to .csv file with data for helical parameter 'shift'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_slide (str): Path to .csv file with data for helical parameter 'slide'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_rise (str): Path to .csv file with data for helical parameter 'rise'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_tilt (str): Path to .csv file with data for helical parameter 'tilt'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_roll (str): Path to .csv file with data for helical parameter 'roll'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_twist (str): Path to .csv file with data for helical parameter 'twist'. File type: input. Accepted formats: csv (edam:format_3752).
        output_csv_path (str): Path to directory where output is saved. File type: output. Accepted formats: csv (edam:format_3752).
        properties (dict):
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_dna.dna.correlation import HelParCorrelation

            HelParCorrelation(
                input_filename_shift='path/to/shift.csv',
                input_filename_slide='path/to/slide.csv',
                input_filename_rise='path/to/rise.csv',
                input_filename_tilt='path/to/tilt.csv',
                input_filename_roll='path/to/roll.csv',
                input_filename_twist='path/to/twist.csv',
                output_csv_path='path/to/output/file.csv',
                properties=prop)

        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_filename_shift, input_filename_slide,
                 input_filename_rise, input_filename_tilt,
                 input_filename_roll, input_filename_twist,
                 output_csv_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {
                'input_filename_shift': input_filename_shift,
                'input_filename_slide': input_filename_slide,
                'input_filename_rise': input_filename_rise,
                'input_filename_tilt': input_filename_tilt,
                'input_filename_roll': input_filename_roll,
                'input_filename_twist': input_filename_twist
            },
            'out': {
                'output_csv_path': output_csv_path,
            }
        }

        self.properties = properties

        # Properties common in all BB
        self.can_write_console_log = properties.get(
            'can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')
        self.remove_tmp = properties.get('remove_tmp', True)
        self.restart = properties.get('restart', False)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`HelParCorrelation <dna.correlation.HelParCorrelation>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)

        # Restart
        if self.restart:
            output_file_list = [self.io_dict['out']['output_csv_path']]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' %
                       self.step, out_log, self.global_log)
                return 0

        # read input
        shift = load_data(self.io_dict["in"]["input_filename_shift"])
        slide = load_data(self.io_dict["in"]["input_filename_slide"])
        rise = load_data(self.io_dict["in"]["input_filename_rise"])
        tilt = load_data(self.io_dict["in"]["input_filename_tilt"])
        roll = load_data(self.io_dict["in"]["input_filename_roll"])
        twist = load_data(self.io_dict["in"]["input_filename_twist"])

        # make matrix
        coordinates = ["shift", "slide", "rise", "tilt", "roll", "twist"]
        corr_matrix = pd.DataFrame(
            np.eye(6, 6), index=coordinates, columns=coordinates)

        # shift
        corr_matrix["shift"]["slide"] = shift.corrwith(slide, method="pearson")
        corr_matrix["shift"]["rise"] = shift.corrwith(rise, method="pearson")
        corr_matrix["shift"]["tilt"] = shift.corrwith(
            tilt, method=self.circlineal)
        corr_matrix["shift"]["roll"] = shift.corrwith(
            roll, method=self.circlineal)
        corr_matrix["shift"]["twist"] = shift.corrwith(
            twist, method=self.circlineal)
        # symmetric values
        corr_matrix["slide"]["shift"] = corr_matrix["shift"]["slide"]
        corr_matrix["rise"]["shift"] = corr_matrix["shift"]["rise"]
        corr_matrix["tilt"]["shift"] = corr_matrix["shift"]["tilt"]
        corr_matrix["roll"]["shift"] = corr_matrix["shift"]["roll"]
        corr_matrix["twist"]["shift"] = corr_matrix["shift"]["twist"]

        # slide
        corr_matrix["slide"]["rise"] = slide.corrwith(rise, method="pearson")
        corr_matrix["slide"]["tilt"] = slide.corrwith(
            tilt, method=self.circlineal)
        corr_matrix["slide"]["roll"] = slide.corrwith(
            roll, method=self.circlineal)
        corr_matrix["slide"]["twist"] = slide.corrwith(
            twist, method=self.circlineal)
        # symmetric values
        corr_matrix["rise"]["slide"] = corr_matrix["slide"]["rise"]
        corr_matrix["tilt"]["slide"] = corr_matrix["slide"]["tilt"]
        corr_matrix["roll"]["slide"] = corr_matrix["slide"]["roll"]
        corr_matrix["twist"]["slide"] = corr_matrix["slide"]["twist"]

        # rise
        corr_matrix["rise"]["tilt"] = rise.corrwith(
            tilt, method=self.circlineal)
        corr_matrix["rise"]["roll"] = rise.corrwith(
            roll, method=self.circlineal)
        corr_matrix["rise"]["twist"] = rise.corrwith(
            twist, method=self.circlineal)
        # symmetric values
        corr_matrix["tilt"]["rise"] = corr_matrix["rise"]["tilt"]
        corr_matrix["roll"]["rise"] = corr_matrix["rise"]["roll"]
        corr_matrix["twist"]["rise"] = corr_matrix["rise"]["twist"]

        # tilt
        corr_matrix["tilt"]["roll"] = tilt.corrwith(roll, method=self.circular)
        corr_matrix["tilt"]["twist"] = tilt.corrwith(
            twist, method=self.circular)
        # symmetric values
        corr_matrix["roll"]["tilt"] = corr_matrix["tilt"]["roll"]
        corr_matrix["twist"]["tilt"] = corr_matrix["tilt"]["twist"]

        # roll
        corr_matrix["roll"]["twist"] = roll.corrwith(
            twist, method=self.circular)
        # symmetric values
        corr_matrix["twist"]["roll"] = corr_matrix["roll"]["twist"]

        # save csv data
        corr_matrix.to_csv(Path(self.io_dict["out"]["output_csv_path"]))

        return 0

    def get_corr_method(self, corrtype1, corrtype2):
        if corrtype1 == "circular" and corrtype2 == "linear":
            method = self.circlineal
        if corrtype1 == "linear" and corrtype2 == "circular":
            method = self.circlineal
        elif corrtype1 == "circular" and corrtype2 == "circular":
            method = self.circular
        else:
            method = "pearson"
        return method

    @staticmethod
    def circular(x1, x2):
        x1 = x1 * np.pi / 180
        x2 = x2 * np.pi / 180
        diff_1 = np.sin(x1 - x1.mean())
        diff_2 = np.sin(x2 - x2.mean())
        num = (diff_1 * diff_2).sum()
        den = np.sqrt((diff_1 ** 2).sum() * (diff_2 ** 2).sum())
        return num / den

    @staticmethod
    def circlineal(x1, x2):
        x2 = x2 * np.pi / 180
        rc = np.corrcoef(x1, np.cos(x2))[1, 0]
        rs = np.corrcoef(x1, np.sin(x2))[1, 0]
        rcs = np.corrcoef(np.sin(x2), np.cos(x2))[1, 0]
        num = (rc ** 2) + (rs ** 2) - 2 * rc * rs * rcs
        den = 1 - (rcs ** 2)
        correlation = np.sqrt(num / den)
        if np.corrcoef(x1, x2)[1, 0] < 0:
            correlation *= -1
        return correlation


def helparcorrelation(
        input_filename_shift: str, input_filename_slide: str,
        input_filename_rise: str, input_filename_tilt: str,
        input_filename_roll: str, input_filename_twist: str,
        output_csv_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`HelParCorrelation <dna.correlation.HelParCorrelation>` class and
    execute the :meth:`launch() <dna.correlation.HelParCorrelation.launch>` method."""

    return HelParCorrelation(
        input_filename_shift=input_filename_shift,
        input_filename_slide=input_filename_slide,
        input_filename_rise=input_filename_rise,
        input_filename_tilt=input_filename_tilt,
        input_filename_roll=input_filename_roll,
        input_filename_twist=input_filename_twist,
        output_csv_path=output_csv_path,
        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Load helical parameter file and save base data individually.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_filename_shift', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--input_filename_slide', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--input_filename_rise', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--input_filename_tilt', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--input_filename_roll', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--input_filename_twist', required=True,
                               help='Path to csv file with inputs. Accepted formats: csv.')
    required_args.add_argument('--output_csv_path', required=True,
                               help='Path to output file. Accepted formats: csv.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    helparcorrelation(
        input_filename_shift=args.input_filename_shift,
        input_filename_slide=args.input_filename_slide,
        input_filename_rise=args.input_filename_rise,
        input_filename_tilt=args.input_filename_tilt,
        input_filename_roll=args.input_filename_roll,
        input_filename_twist=args.input_filename_twist,
        output_csv_path=args.output_csv_path,
        properties=properties)


if __name__ == '__main__':
    main()
