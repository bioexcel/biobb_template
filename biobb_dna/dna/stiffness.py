#!/usr/bin/env python3

"""Module containing the HelParStiffness class and the command line interface."""
import argparse
from pathlib import Path

import pandas as pd
import numpy as np

from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_dna.dna.loader import load_data


class HelParStiffness():
    """
    | biobb_dna HelParStiffness
    | 

    Args:        
        input_filename_shift (str): Path to .csv file with data for helical parameter 'shift'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_slide (str): Path to .csv file with data for helical parameter 'slide'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_rise (str): Path to .csv file with data for helical parameter 'rise'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_tilt (str): Path to .csv file with data for helical parameter 'tilt'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_roll (str): Path to .csv file with data for helical parameter 'roll'. File type: input. Accepted formats: csv (edam:format_3752).
        input_filename_twist (str): Path to .csv file with data for helical parameter 'twist'. File type: input. Accepted formats: csv (edam:format_3752).
        output_covariance_path (str): Path to directory where covariance output file is saved as a csv file. File type: output. Accepted formats: csv (edam:format_3752).
        output_stiffness_path (str): Path to directory where stiffness output file is saved as a csv file. File type: output. Accepted formats: csv (edam:format_3752).
        output_fctes_path (str): Path to directory where force constants output file is saved as a csv file. File type: output. Accepted formats: csv (edam:format_3752).
        output_averages_path (str): Path to directory where averages output file is saved as a csv file. File type: output. Accepted formats: csv (edam:format_3752).
        properties (dict):
            * **KT** (*float*) - (0.592186827) Value of Boltzmann temperature factor.
            * **scaling** (*list*) - ([1, 1, 1, 10.6, 10.6, 10.6]) Values by which to scale stiffness. Positions correspond to helical parameters in the order: shift, slide, rise, tilt, roll, twist.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_dna.dna.stiffness import HelParStiffness

            prop = { 
                'KT': 0.592186827,
                'scaling': [1, 1, 1, 10.6, 10.6, 10.6]
            }
            HelParStiffness(
                input_filename_shift='path/to/shift.csv',
                input_filename_slide='path/to/slide.csv',
                input_filename_rise='path/to/rise.csv',
                input_filename_tilt='path/to/tilt.csv',
                input_filename_roll='path/to/roll.csv',
                input_filename_twist='path/to/twist.csv',
                output_covariance_path='path/to/output/covariance.csv',
                output_stiffness_path='path/to/output/stiffness.csv',
                output_fctes_path='path/to/output/fctes.csv',
                output_averages_path='path/to/output/averages.csv',
                properties=prop)

        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_filename_shift, input_filename_slide,
                 input_filename_rise, input_filename_tilt,
                 input_filename_roll, input_filename_twist,
                 output_covariance_path, output_stiffness_path,
                 output_fctes_path, output_averages_path,
                 properties=None, **kwargs) -> None:
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
                'output_covariance_path': output_covariance_path,
                'output_stiffness_path': output_stiffness_path,
                'output_fctes_path': output_fctes_path,
                'output_averages_path': output_averages_path
            }
        }

        self.properties = properties
        self.KT = properties.get(
            "KT", 0.592186827)
        self.scaling = properties.get(
            "scaling", [1, 1, 1, 10.6, 10.6, 10.6])

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
        """Execute the :class:`HelParStiffness <dna.stiffness.HelParStiffness>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)

        # Restart
        if self.restart:
            output_file_list = [self.io_dict['out']['output_path']]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' %
                       self.step, out_log, self.global_log)
                return 0

        # read input
        shift = load_data(
            self.io_dict["in"]["input_filename_shift"])
        slide = load_data(
            self.io_dict["in"]["input_filename_slide"])
        rise = load_data(
            self.io_dict["in"]["input_filename_rise"])
        tilt = load_data(
            self.io_dict["in"]["input_filename_tilt"])
        roll = load_data(
            self.io_dict["in"]["input_filename_roll"])
        twist = load_data(
            self.io_dict["in"]["input_filename_twist"])

        # calculate mean for each helpar input file
        SH_av = shift.mean().item()
        SL_av = slide.mean().item()
        RS_av = rise.mean().item()
        TL_av = self.circ_avg(tilt).item()
        RL_av = self.circ_avg(roll).item()
        TW_av = self.circ_avg(twist).item()

        # build matrix cols_arr from helpar input data files
        coordinates = ["shift", "slide", "rise", "tilt", "roll", "twist"]
        helpar_matrix = pd.concat(
            [shift, slide, rise, tilt, roll, twist], axis=1)
        helpar_matrix.columns = [
            f"{c}_{h}" for c, h in zip(coordinates, helpar_matrix.columns)]
        # covariance
        cov_df = helpar_matrix.cov()
        # stiffness
        stiff = np.linalg.inv(cov_df) * self.KT
        stiff_df = pd.DataFrame(
            stiff,
            columns=cov_df.columns,
            index=cov_df.index)
        averages = [SH_av, SL_av, RS_av, TL_av, RL_av, TW_av]
        avg_df = pd.DataFrame(averages, index=coordinates, columns=["avg"])
        # stiffness matrix diagonal with scaling
        stiff_diag = np.diagonal(stiff) * np.array(self.scaling)
        stiff_diag = np.append(
            stiff_diag, [np.product(stiff_diag), np.sum(stiff_diag)])
        stiff_diag_df = pd.DataFrame(
            stiff_diag,
            index=list(cov_df.index)+["product", "sum"],
            columns=["fctes"])

        # save csv data
        cov_df.to_csv(Path(self.io_dict["out"]["output_covariance_path"]))
        stiff_df.to_csv(Path(self.io_dict["out"]["output_stiffness_path"]))
        stiff_diag_df.to_csv(Path(self.io_dict["out"]["output_fctes_path"]))
        avg_df.to_csv(Path(self.io_dict["out"]["output_averages_path"]))

        return 0

    @staticmethod
    def circ_avg(xarr, degrees=True):
        n = len(xarr)
        if degrees:
            # convert to radians
            xarr = xarr * np.pi / 180
        av = np.arctan2(
            (np.sum(np.sin(xarr)))/n,
            (np.sum(np.cos(xarr)))/n) * 180 / np.pi
        return av


def helparstiffness(
        input_filename_shift: str, input_filename_slide: str,
        input_filename_rise: str, input_filename_tilt: str,
        input_filename_roll: str, input_filename_twist: str,
        output_covariance_path: str, output_stiffness_path: str,
        output_fctes_path: str, output_averages_path: str,
        properties: dict = None, **kwargs) -> int:
    """Create :class:`HelParStiffness <dna.stiffness.HelParStiffness>` class and
    execute the :meth:`launch() <dna.stiffness.HelParStiffness.launch>` method."""

    return HelParStiffness(
        input_filename_shift=input_filename_shift,
        input_filename_slide=input_filename_slide,
        input_filename_rise=input_filename_rise,
        input_filename_tilt=input_filename_tilt,
        input_filename_roll=input_filename_roll,
        input_filename_twist=input_filename_twist,
        output_covariance_path=output_covariance_path,
        output_stiffness_path=output_stiffness_path,
        output_fctes_path=output_fctes_path,
        output_averages_path=output_averages_path,
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
    required_args.add_argument('--output_covariance_path', required=True,
                               help='Path to output covariance data file. Accepted formats: csv.')
    required_args.add_argument('--output_stiffness_path', required=True,
                               help='Path to output stiffness data file. Accepted formats: csv.')
    required_args.add_argument('--output_fctes_path', required=True,
                               help='Path to output force constants data file. Accepted formats: csv.')
    required_args.add_argument('--output_averages_path', required=True,
                               help='Path to output averages data file. Accepted formats: csv.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    helparstiffness(
        input_filename_shift=args.input_filename_shift,
        input_filename_slide=args.input_filename_slide,
        input_filename_rise=args.input_filename_rise,
        input_filename_tilt=args.input_filename_tilt,
        input_filename_roll=args.input_filename_roll,
        input_filename_twist=args.input_filename_twist,
        output_covariance_path=args.output_covariance_path,
        output_stiffness_path=args.output_stiffness_path,
        output_fctes_path=args.output_fctes_path,
        output_averages_path=args.output_averages_path,
        properties=properties)


if __name__ == '__main__':
    main()
