#!/usr/bin/env python3

"""Module containing the HelParTimeSeries class and the command line interface."""
import argparse
import shutil
import zipfile
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_dna.dna.loader import read_series


class HelParTimeSeries():
    """
    | biobb_dna HelParTimeSeries
    | Load .ser file for a given helical parameter, read and analyze each column corresponding to a base. Created time series and histogram plots for each base.

    Args:
        input_ser_path (str): Path to .ser file for helical parameter. File is expected to be a table, with the first column being an index and the rest the helical parameter values for each base/basepair. File type: input. Accepted formats: ser
        output_zip_path (str): Path to output .zip files where data is saved. File type: output. Accepted formats: .zip
        properties (dict):
            * **strand1** (*str*) - Nucleic acid sequence for the first strand (5'->3') corresponding to the input .ser file. Length of sequence is expected to be the same as the total number of columns in the .ser file, minus the index column (even if later on a subset of columns is selected with the *usecols* option).
            * **strand2** (*str*) - Nucleic acid sequence for the second strand (3'->5') corresponding to the input .ser file.
            * **bins** (*int* or *sequence* or *str*) - Bins for histogram. Parameter has same options as matplotlib.pyplot.hist.
            * **helpar_name** (*str*) - (helical_parameter) helical parameter name.
            * **stride** (*int*) - (1000) granularity of the number of snapshots for plotting time series.
            * **usecols** (*list*) - (None) list of column indices to use.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_dna.dna.timeseries import HelParTimeSeries

            prop = {
                'helpar_name': 'twist',
                'usecols': [1,2,3,4,5],
                'strand1': 'GCAACGTGCTATGGAAGC',
                'strand2': 'GCTTCCATAGCACGTTGC'
            }
            HelParTimeSeries(
                input_ser_path='/path/to/twist.ser',
                output_zip_path='/path/to/output/file.zip'
                properties=prop)

        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_ser_path, output_zip_path,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {
                'input_ser_path': input_ser_path,
            },
            'out': {
                'output_zip_path': output_zip_path
            }
        }

        self.properties = properties
        self.strand1 = properties.get("strand1")
        self.strand2 = properties.get("strand2")
        self.bins = properties.get("bins", "auto")
        self.stride = properties.get(
            "stride", 10)
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
        """Execute the :class:`HelParTimeSeries <dna.timeseries.HelParTimeSeries>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)

        # Restart
        if self.restart:
            output_file_list = [self.io_dict['out']['output_zip_path']]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' %
                       self.step, out_log, self.global_log)
                return 0

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir(prefix="timeseries_")
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        # Copy input_ser_path to temporary folder
        shutil.copy(self.io_dict['in']['input_ser_path'], self.tmp_folder)

        hp_basepairs = ["shift", "slide", "rise", "tilt", "roll", "twist"]
        hp_singlebases = [
            "buckle", "opening", "propel", "shear", "stagger", "stretch"]
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
        strand1 = self.strand1
        strand2 = self.strand2[::-1]

        # read input .ser file and create dataframe
        ser_data = read_series(
            self.io_dict['in']['input_ser_path'])
        if self.usecols is None:
            # discard first and last column
            ser_data = ser_data[ser_data.columns[1:-1]]
            strand1 = strand1[1:-1]
            strand2 = strand2[1:-1]
            subunits = [
                f"{strand1[i:i+1+step]}{strand2[i:i+1+step][::-1]}"
                for i in range(len(ser_data.columns) - step)]
            ser_data = ser_data[ser_data.columns[:len(subunits)]]
            ser_data.columns = subunits
        else:
            ser_data = ser_data[self.usecols]
            subunits = [
                f"{strand1[i:i+1+step]}{strand2[i:i+1+step][::-1]}"
                for i in [c-step for c in self.usecols]]
            ser_data.columns = subunits

        # write output files for all selected bases (one per column)
        zf = zipfile.ZipFile(
            Path(self.io_dict["out"]["output_zip_path"]), "w")
        for col in ser_data.columns:
            # unstack columns to prevent errors from repeated base pairs
            column_data = (
                ser_data[[col]]
                .unstack()
                .dropna()
                .reset_index(drop=True))
            column_data.name = col
            fu.log(f"Computing base number {col}...")

            # column series
            series_colfn = f"series_{self.helpar_name}_{col}"
            column_data.to_csv(
                Path(self.tmp_folder) / f"{series_colfn}.csv")
            # save table
            zf.write(
                Path(self.tmp_folder) / f"{series_colfn}.csv", arcname=f"{series_colfn}.csv")

            fig, axs = plt.subplots(1, 1, dpi=300, tight_layout=True)
            reduced_data = column_data.iloc[::self.stride]
            axs.plot(reduced_data.index, reduced_data.to_numpy())
            axs.set_xlabel("Time (Snapshots)")
            axs.set_ylabel(f"{self.helpar_name} ({hp_unit})")
            axs.set_title(
                f"Helical Parameter vs Time: {self.helpar_name} "
                f"(base pair {'step' if step==1 else ''} {col})")
            fig.savefig(
                Path(self.tmp_folder) / f"{series_colfn}.jpg", format="jpg")
            # save plot
            zf.write(
                Path(self.tmp_folder) / f"{series_colfn}.jpg", arcname=f"{series_colfn}.jpg")
            plt.close()

            # columns histogram
            hist_colfn = f"hist_{self.helpar_name}_{col}"
            fig, axs = plt.subplots(1, 1, dpi=300, tight_layout=True)
            ybins, x, _ = axs.hist(column_data, bins=self.bins)
            pd.DataFrame({self.helpar_name: x[:-1], "density": ybins}).to_csv(
                Path(self.tmp_folder) / f"{hist_colfn}.csv",
                index=False)
            # save table
            zf.write(
                Path(self.tmp_folder) / f"{hist_colfn}.csv",
                arcname=f"{hist_colfn}.csv")

            axs.set_ylabel("density")
            axs.set_xlabel(f"{self.helpar_name} ({hp_unit})")
            fig.savefig(
                Path(self.tmp_folder) / f"{hist_colfn}.jpg",
                format="jpg")
            # save plot
            zf.write(
                Path(self.tmp_folder) / f"{hist_colfn}.jpg",
                arcname=f"{hist_colfn}.jpg")
            plt.close()
        zf.close()

        # Remove temporary file(s)
        if self.remove_tmp:
            fu.rm(self.tmp_folder)
            fu.log('Removed: %s' % str(self.tmp_folder), out_log)

        return 0


def helpartimeseries(
        input_ser_path: str, output_zip_path: str,
        properties: dict = None, **kwargs) -> int:
    """Create :class:`HelParTimeSeries <dna.timeseries.HelParTimeSeries>` class and
    execute the :meth:`launch() <dna.timeseries.HelParTimeSeries.launch>` method."""

    return HelParTimeSeries(
        input_ser_path=input_ser_path,
        output_zip_path=output_zip_path,
        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Load helical parameter file and save base data individually.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False,
                        help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_ser_path', required=True,
                               help='Helical parameter input ser file path. Accepted formats: ser.')
    required_args.add_argument('--output_zip_path', required=True,
                               help='Path to output directory.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    helpartimeseries(
        input_ser_path=args.input_ser_path,
        output_zip_path=args.output_zip_path,
        properties=properties)


if __name__ == '__main__':
    main()
