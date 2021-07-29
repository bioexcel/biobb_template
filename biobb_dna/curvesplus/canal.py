#!/usr/bin/env python3

"""Module containing the Canal class and the command line interface."""
import zipfile
import argparse
from pathlib import Path
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper


class Canal():
    """
    | biobb_dna Canal
    | Wrapper for the Canal executable that is part of the Curves+ software suite. 

    Args:        
        input_cda_file (str): Input .cda file, from Cur+ output. File type: input. Accepted formats: cda.
        output_zip_path (str): zip filename for output files. File type: output.  Accepted formats: zip.
        properties (dic):
            * **bases** (*base*) - (None) sequence of bases to be searched for in the I/P data (default is blank, meaning no specified sequence). 
            * **itst** (*int*) - (0) Iteration start index.
            * **itnd** (*int*) - (0) Iteration end index.
            * **itdel** (*int*) - (1) Iteration delimiter. 
            * **lev1** (*int*) - (0) Lower base level limit (i.e. base pairs) used for analysis.
            * **lev2** (*int*) - (0) Upper base level limit used for analysis. If lev1 > 0 and lev2 = 0, lev2 is set to lev1 (i.e. analyze lev1 only). If lev1=lev2=0, lev1 is set to 1 and lev2 is set to the length of the oligmer (i.e. analyze all levels).
            * **nastr** (*str*) - ('NA') character string used to indicate missing data in .ser files.
            * **cormin** (*float*) - (0.6) minimal absolute value for printing linear correlation coefficients between pairs of analyzed variables.
            * **series** (*str*) - ('.f.') if '.t.' then output spatial or time series data. Only possible for the analysis of single structures or single trajectories.
            * **histo** (*str*) - ('.f.') if '.t.' then output histogram data.
            * **corr** (*str*) - ('.f.') if '.t.' than output linear correlation coefficients between all variables.
            * **sequence** (*str*) - (Optional) sequence of the first strand of the corresponding DNA fragment, for each .cda file. If not given it will be parsed from .cda file.
            * **canal_exec** (*str*) - ('Canal') Path to Canal executable, otherwise the program wil look for Canal executable in the binaries folder.
    Examples:
        This is a use example of how to use the building block from Python::
            from biobb_dna.curvesplus.canal import canal
            prop = { 
                'series': '.t.',
                'histo': '.t.',
                'sequence': 'CGCGAATTCGCG'
            }
            canal(
                input_cda_file='/path/to/curves/output.cda',
                output_zip_path='/path/to/output.zip',
                properties=prop)
    Info:
        * wrapped_software:
            * name: Canal
            * version: >=2.6
            * license: BSD 3-Clause
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_cda_file, output_zip_path,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {'input_cda_file': input_cda_file},
            'out': {'output_zip_path': output_zip_path}
        }

        # Properties specific for BB
        self.bases = properties.get('bases', None)
        self.nastr = properties.get('nastr', None)
        self.cormin = properties.get('cormin', 0.6)
        self.lev1 = properties.get('lev1', 0)
        self.lev2 = properties.get('lev2', 0)
        self.itst = properties.get('itst', 0)
        self.itnd = properties.get('itnd', 0)
        self.itdel = properties.get('itdel', 1)
        self.series = properties.get('series', '.f.')
        self.histo = properties.get('histo', '.f.')
        self.corr = properties.get('corr', '.f.')
        self.sequence = properties.get('sequence', None)
        self.canal_exec = properties.get('canal_exec', 'Canal')
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
        """Execute the :class:`Canal <biobb_dna.curvesplus.Canal>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)
        if self.sequence is None:
            cda_lines = Path(
                self.io_dict['in']['input_cda_file']).read_text().splitlines()
            for line in cda_lines:
                if line.strip().startswith("Strand  1"):
                    self.sequence = line.split(" ")[-1]
        # Restart
        if self.restart:
            output_file_list = [self.io_dict['out']['output_zip_path']]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' %
                       self.step, out_log, self.global_log)
                return 0

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        # create intructions
        instructions = [
            f"{self.canal_exec} <<! ",
            "&inp",
            f"  lis={Path(self.tmp_folder) / 'canal_output'},"]
        if self.bases is not None:
            # add topology file if needed
            fu.log('Appending sequence of bases to be searched to command',
                   out_log, self.global_log)
            instructions.append(f"  seq={self.bases},")
        if self.nastr is not None:
            # add topology file if needed
            fu.log('Adding null values string specification to command',
                   out_log, self.global_log)
            instructions.append(f"  nastr={self.nastr},")

        instructions = instructions + [
            f"  cormin={self.cormin},",
            f"  lev1={self.lev1},lev2={self.lev2},",
            f"  itst={self.itst},itnd={self.itnd},itdel={self.itdel},",
            f"  histo={self.histo},",
            f"  series={self.series},",
            f"  corr={self.corr},",
            "&end",
            f"{self.io_dict['in']['input_cda_file']} {self.sequence}",
            "!"]

        cmd = ["\n".join(instructions)]
        fu.log('Creating command line with instructions and required arguments',
               out_log, self.global_log)
        # Launch execution
        returncode = cmd_wrapper.CmdWrapper(
            cmd, out_log, err_log, self.global_log).launch()

        # create zipfile and wirte output inside
        zf = zipfile.ZipFile(
            Path(self.io_dict["out"]["output_zip_path"]), "w")
        for canal_outfile in Path(self.tmp_folder).glob("canal_output*"):
            zf.write(
                canal_outfile,
                arcname=canal_outfile.name)
        zf.close()

        # Remove temporary file(s)
        if self.remove_tmp:
            fu.rm(self.tmp_folder)
            fu.log('Removed: %s' % str(self.tmp_folder), out_log)

        return returncode


def canal(input_cda_file: str, output_zip_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Canal <biobb_dna.curvesplus.canal.Canal>` class and
    execute the :meth:`launch() <biobb_dna.curvesplus.canal.Canal.launch>` method."""

    return Canal(
        input_cda_file=input_cda_file,
        output_zip_path=output_zip_path,
        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Description for the template module.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_cda_file', required=True,
                               help='Trajectory or PDB input file. Accepted formats: trj, pdb.')
    required_args.add_argument('--output_zip_path', required=True,
                               help='Root filename to give to output files (without the .lis extension). Accepted formats: str.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    canal(
        input_cda_file=args.input_cda_file,
        output_zip_path=args.output_zip_path,
        properties=properties)


if __name__ == '__main__':
    main()
