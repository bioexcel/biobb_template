#!/usr/bin/env python3

"""Module containing the HelParBimodality class and the command line interface."""
import shutil
import argparse

import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture

from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_dna.dna.loader import load_data


class HelParBimodality():
    """
    | biobb_dna HelParBimodality
    | 

    Args:        
        input_file_path (str): Path to .csv or .zip file with helical parameter data. File type: input. Accepted formats: csv (edam:format_3752), zip (edam:format_3987).
        output_csv_path (str): Path to .csv file where output is saved. File type: output. Accepted formats: csv (edam:format_3752).
        properties (dict):
            * **inner_file** (*str*) - (None) If .zip file is passed to input_filename, specify name of .csv file inside to be used.
            * **confidence_level** (*float*) - (5.0) Confidence level for Byes Factor test (in percentage).
            * **max_iter** (*int*) - (400) Number of maximum iterations for EM algorithm.
            * **tol** (*float*) - (1e-5) Tolerance value for EM algorithm.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.1

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_dna.dna.bimodality import HelParBimodality

            prop = { 
                'max_iter': 500,
                'inner_file': 'filename.csv'
            }
            HelParBimodality(
                input_file_path='/path/to/input.zip',
                output_csv_path='/path/to/output.csv',
                properties=prop)

        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_file_path, output_csv_path,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {
                'input_file_path': input_file_path
            },
            'out': {
                'output_csv_path': output_csv_path
            }
        }

        self.confidence_level = properties.get(
            "confidence_level", 5.0)
        self.max_iter = properties.get(
            "max_iter", 400)
        self.tol = properties.get(
            "tol", 1e-5)
        self.properties = properties

        # Properties common in all BB
        self.inner_file = properties.get('inner_file', None)
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
        """Execute the :class:`HelParBimodality <dna.bimodality.HelParBimodality>` object."""

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

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir(prefix="bimodality_")
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        # Copy input_file_path1 to temporary folder
        shutil.copy(self.io_dict['in']['input_file_path'], self.tmp_folder)

        # read input
        data = load_data(
            data_filename=self.io_dict['in']['input_file_path'],
            inner_file=self.inner_file)
        means, variances, bics, weights = self.fit_to_model(data)
        uninormal, binormal, insuf_ev = self.bayes_factor_criteria(
            bics[0], bics[1])

        if binormal:
            maxm = np.argmax(means[1])
            minm = np.argmin(means[1])
            mean1 = means[1][minm]
            var1 = variances[1][minm]
            w1 = weights[1][minm]
            mean2 = means[1][maxm]
            var2 = variances[1][maxm]
            w2 = weights[1][maxm]
            bimodal = self.helguero_theorem(mean1, mean2, var1, var2)
        else:
            mean1 = means[0][0]
            var1 = variances[0][0]
            w1 = weights[0][0]
            mean2, var2, w2 = np.nan, np.nan, 0
            bimodal = False
        info = dict(
            binormal=binormal,
            uninormal=uninormal,
            insuf_ev=insuf_ev,
            bimodal=bimodal,
            mean1=mean1,
            mean2=mean2,
            var1=var1,
            var2=var2,
            w1=w1,
            w2=w2)

        pd.DataFrame(info, index=data.columns).to_csv(
            self.io_dict["out"]["output_csv_path"])

        # Remove temporary file(s)
        if self.remove_tmp:
            fu.rm(self.tmp_folder)
            fu.log('Removed: %s' % str(self.tmp_folder), out_log)

        return 0

    def fit_to_model(self, data):
        """
        Fit data to Gaussian Mixture models.
        Return dictionary with distribution data.
        """
        means = []
        variances = []
        bics = []
        weights = []
        for n_components in (1, 2):
            gmm = GaussianMixture(
                n_components=n_components,
                max_iter=self.max_iter,
                tol=self.tol)
            gmm = gmm.fit(data)
            m = gmm.means_.flatten()
            v = gmm.covariances_.flatten()
            b = gmm.bic(data)
            w = gmm.weights_.flatten()
            means.append(m)
            variances.append(v)
            bics.append(b)
            weights.append(w)
        return means, variances, bics, weights

    def bayes_factor_criteria(self, bic1, bic2):
        diff_bic = bic2 - bic1
        # probability of a two-component model
        p = 1 / (1 + np.exp(0.5*diff_bic))
        if p == np.nan:
            if bic1 == np.nan:
                p = 1
            elif bic2 == np.nan:
                p = 0

        uninormal = p < (self.confidence_level / 100)
        binormal = p > (1 - (self.confidence_level / 100))
        insuf_ev = True if (not uninormal and not binormal) else False
        return uninormal, binormal, insuf_ev

    def helguero_theorem(self, mean1, mean2, var1, var2):
        r = var1 / var2
        separation_factor = np.sqrt(
            -2 + 3*r + 3*r**2 - 2*r**3 + 2*(1 - r + r**2)**1.5
        ) / (
            np.sqrt(r)*(1+np.sqrt(r))
        )
        bimodal = abs(mean2-mean1) > separation_factor * \
            (np.sqrt(var1) + np.sqrt(var2))
        return bimodal


def helparbimodality(
        input_file_path: str, output_csv_path: str,
        properties: dict = None, **kwargs) -> int:
    """Create :class:`HelParBimodality <dna.bimodality.HelParBimodality>` class and
    execute the :meth:`launch() <dna.bimodality.HelParBimodality.launch>` method."""

    return HelParBimodality(
        input_file_path=input_file_path,
        output_csv_path=output_csv_path,
        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Load helical parameter file and save base data individually.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_file_path', required=True,
                               help='Path to csv or zip file with input. Accepted formats: csv, zip.')
    required_args.add_argument('--output_csv_path', required=True,
                               help='Filename and/or path of output csv file.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    helparbimodality(
        input_file_path=args.input_file_path,
        output_csv_path=args.output_csv_path,
        properties=properties)


if __name__ == '__main__':
    main()
