# !/usr/bin/env python3
from biobb_dna.dna.loader import read_series
from biobb_common.tools.file_utils import launchlogger
from biobb_common.tools import file_utils as fu
from biobb_common.configuration import settings
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import zipfile
import shutil
import argparse


"""Module containing the HelParAverages class and the command line interface."""


class HelParAverages():
    """
    | biobb_dna HelParAverages
    | Load .ser file for a given helical parameter and read each column corresponding to a base calculating average over each one.

    Args:        
        input_ser_path (str): Path to .ser file for helical parameter. File is expected to be a table, with the first column being an index and the rest the helical parameter values for each base/basepair. File type: input. Accepted formats: ser
        output_csv_path (str): Path to .csv file where output is saved. File type: output. Accepted formats: csv (edam:format_3752).
        output_jpg_path (str): Path to .jpg file where output is saved. File type: output. Accepted formats: jpg (edam:format_3579).
        properties (dict):
            * **strand1** (*str*) - Nucleic acid sequence for the first strand corresponding to the input .ser file. Length of sequence is expected to be the same as the total number of columns in the .ser file, minus the index column (even if later on a subset of columns is selected with the *usecols* option).
            * **strand2** (*str*) - Nucleic acid sequence for the second strand corresponding to the input .ser file.
            * **helpar_name** (*str*) - (helical_parameter) helical parameter name.
            * **stride** (*int*) - (1000) granularity of the number of snapshots for plotting time series.
            * **usecols** (*list*) - (None) list of column indices to use.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_dna.dna.averages import HelParAverages

            prop = { 
                'helpar_name': 'twist',
                'usecols': [1,2],
                'strand1': 'GCAT',
                'strand2': 'ATGC'
            }
            HelParAverages(
                input_ser_path='/path/to/twist.ser',
                output_csv_path='/path/to/table/output.csv',
                output_jpg_path='/path/to/table/output.jpg',
                properties=prop)

        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_ser_path, output_csv_path, output_jpg_path,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {
                'input_ser_path': input_ser_path,
            },
            'out': {
                'output_csv_path': output_csv_path,
                'output_jpg_path': output_jpg_path
            }
        }

        self.properties = properties
        self.strand1 = properties.get("strand1")
        self.strand2 = properties.get("strand2")
        self.stride = properties.get(
            "stride", 1000)
        self.usecols = properties.get(
            "usecols", None)
        helpar_name = properties.get(
            "helpar_name", None)

        if helpar_name is None:
            for hp in [
                    "shift", "slide", "rise",
                    "tilt", "roll", "twist",
                    "buckle", "opening", "propel",
                    "shear", "stagger", "stretch"]:
                if hp in input_ser_path:
                    helpar_name = hp
            if helpar_name is None:
                raise ValueError("Helical Parameter name must be specified!")
        self.helpar_name = helpar_name

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
        """Execute the :class:`HelParAverages <dna.averages.HelParAverages>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)

        # Restart
        if self.restart:
            output_file_list = [
                self.io_dict['out']['output_csv_path'],
                self.io_dict['out']['output_jpg_path']]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' %
                       self.step, out_log, self.global_log)
                return 0

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir(prefix="averages_")
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        # Copy input_file_path1 to temporary folder
        shutil.copy(self.io_dict['in']['input_ser_path'], self.tmp_folder)

        # read input .ser file
        ser_data = read_series(
            self.io_dict['in']['input_ser_path'],
            self.usecols)
        # discard first and last column
        ser_data = ser_data[ser_data.columns[1:-1]]

        hp_basepairs = ["shift", "slide", "rise", "tilt", "roll", "twist"]
        hp_singlebases = [
            "shear", "stagger", "stretch", "buckle", "opening", "propel"]
        if self.helpar_name in hp_basepairs:
            step = 1
            if self.helpar_name in ["shift", "slide", "rise"]:
                hp_unit = "Angstroms"
            else:
                hp_unit = "Degrees"
        elif self.helpar_name in hp_singlebases:
            step = 0
            if self.helpar_name in ["shear", "stagger", "stretch"]:
                hp_unit = "Angstroms"
            else:
                hp_unit = "Degrees"

        # discard first and last base(pairs) from strands
        strand1 = self.strand1[1:-1]
        strand2 = self.strand2[::-1][1:-1]
        xlabels = [
            f"{strand1[i:i+1+step]}{strand2[i:i+1+step][::-1]}"
            for i in range(len(ser_data.columns) - step)]

        # write output files for all selected bases
        means = ser_data.mean(axis=0).iloc[:len(xlabels)]
        stds = ser_data.std(axis=0).iloc[:len(xlabels)]

        # save plot
        fig, axs = plt.subplots(1, 1, dpi=300, tight_layout=True)
        axs.errorbar(
            means.index,
            means.to_numpy(),
            yerr=stds.to_numpy(),
            marker="o",
            capsize=5)
        axs.set_xticks(means.index)
        axs.set_xticklabels(xlabels, rotation=90)
        axs.set_xlabel(f"Sequence Base Pair {'Step' if step==1 else ''}")
        axs.set_ylabel(f"{self.helpar_name} ({hp_unit})")
        axs.set_title(
            f"Base Pair {'Step' if step==1 else ''} "
            f"Helical Parameter: {self.helpar_name}")
        fig.savefig(
            self.io_dict['out']['output_jpg_path'],
            format="jpg")

        # save table
        dataset = pd.DataFrame({
            f"Base Pair {'Step' if step==1 else ''}": xlabels,
            "mean": means.to_numpy(),
            "std": stds.to_numpy()})
        dataset.to_csv(
            self.io_dict['out']['output_csv_path'],
            index=False)

        plt.close()

        # Remove temporary file(s)
        if self.remove_tmp:
            fu.rm(self.tmp_folder)
            fu.log('Removed: %s' % str(self.tmp_folder), out_log)

        return 0


def helparaverages(
        input_ser_path: str, output_csv_path: str, output_jpg_path: str,
        properties: dict = None, **kwargs) -> int:
    """Create :class:`HelParAverages <dna.averages.HelParAverages>` class and
    execute the :meth:`launch() <dna.averages.HelParAverages.launch>` method."""

    return HelParAverages(input_ser_path=input_ser_path,
                          output_csv_path=output_csv_path,
                          output_jpg_path=output_jpg_path,
                          properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Load helical parameter file and save base data individually.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_ser_path', required=True,
                               help='Helical parameter input ser file path. Accepted formats: ser.')
    required_args.add_argument('--output_csv_path', required=True,
                               help='Path to output csv file. Accepted formats: csv.')
    required_args.add_argument('--output_jpg_path', required=True,
                               help='Path to output jpg file. Accepted formats: jpg.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    helparaverages(
        input_ser_path=args.input_ser_path,
        output_csv_path=args.output_csv_path,
        output_jpg_path=args.output_jpg_path,
        properties=properties)


if __name__ == '__main__':
    main()
