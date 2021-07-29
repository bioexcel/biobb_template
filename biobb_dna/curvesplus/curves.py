#!/usr/bin/env python3

"""Module containing the Curves class and the command line interface."""
import zipfile
import argparse
import shutil
from pathlib import Path
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper


class Curves():
    """
    | biobb_dna Curves
    | Wrapper for the Cur+ executable  that is part of the Curves+ software suite. 

    Args:        
        input_struc_path (str): Trajectory or PDB input file. File type: input. Accepted formats: trj (edam:format_3910), pdb (edam:format_1476).
        input_top_path (str) (Optional): Topology file, needed along with .trj file (optional). File type: input. Accepted formats: top (edam:format_3881).
        output_zip_path (str): Filename for .zip files containing Curve+ output. File type: output. Accepted formats: zip (edam:format_3987).
        properties (dict):
            * **stdlib_path** (*path*) - ('standard') Path to Curves' standard library files for nucleotides. If not specified will look for 'standard' files in current directory.
            * **itst** (*int*) - (0) Iteration start index.
            * **itnd** (*int*) - (0) Iteration end index.
            * **itdel** (*int*) - (1) Iteration delimiter. 
            * **ions** (*bool*) - (False) If True, helicoidal analysis of ions (or solvent molecules) around solute is carried out.
            * **s1range** (*str*) - (None) Range of first strand. Must be specified in the form "start:end". 
            * **s2range** (*str*) - (None) Range of second strand. Must be specified in the form "start:end".
            * **curves_exec** (*str*) - (Cur+) Path to Curves+ executable, otherwise the program wil look for Cur+ executable in the binaries folder.
    Examples:
        This is a use example of how to use the building block from Python::
            from biobb_dna.curvesplus.curves import curves
            prop = { 
                's1range': '1:12',
                's2range': '24:13', 
            }
            curves(
                input_struc_path='/path/to/structure/file.trj',
                input_top_path='/path/to/topology.top',
                output_zip_path='/path/to/output/root/filename',
                properties=prop)
    Info:
        * wrapped_software:
            * name: Curves
            * version: >=2.6
            * license: BSD 3-Clause
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_struc_path, output_zip_path,
                 input_top_path=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = {
            'in': {
                'input_struc_path': input_struc_path,
                'input_top_path': input_top_path
            },
            'out': {'output_zip_path': output_zip_path}
        }

        # Properties specific for BB
        self.itst = properties.get('itst', 0)
        self.itnd = properties.get('itnd', 0)
        self.itdel = properties.get('itdel', 1)
        self.ions = properties.get('ions', '.f.')
        self.s1range = properties.get('s1range', None)
        self.s2range = properties.get('s2range', None)
        self.curves_exec = properties.get('curves_exec', 'Cur+')
        self.stdlib_path = properties.get('stdlib_path', 'standard')
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
        """Execute the :class:`Curves <biobb_dna.curvesplus.Curves>` object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)
        if self.s1range is None:
            raise ValueError("property 's1range' must be specified!")
        if self.s2range is None:
            raise ValueError("property 's2range' must be specified!")

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

        shutil.copy(self.io_dict['in']['input_struc_path'], self.tmp_folder)
        if self.io_dict['in']['input_top_path'] is not None:
            shutil.copy(self.io_dict['in']['input_top_path'], self.tmp_folder)

       # create intructions
        instructions = [
            "export DYLD_LIBRARY_PATH=$AMBERHOME/lib; ",
            f"{self.curves_exec} <<! ",
            "&inp",
            f"  file={self.io_dict['in']['input_struc_path']},"]
        if self.io_dict['in']['input_top_path'] is not None:
            # add topology file if needed
            fu.log('Appending provided topology to command',
                   out_log, self.global_log)
            instructions.append(
                f"  ftop={self.io_dict['in']['input_top_path']},")

        instructions = instructions + [
            f"  lis={Path(self.tmp_folder) / 'curves_output'},",
            f"  lib={self.stdlib_path},",
            f"  ions={self.ions},",
            f"  itst={self.itst},itnd={self.itnd},itdel={self.itdel},",
            "&end",
            "2 1 -1 0 0",
            f"{self.s1range}",
            f"{self.s2range}",
            "!"
        ]
        cmd = ["\n".join(instructions)]
        fu.log('Creating command line with instructions and required arguments',
               out_log, self.global_log)
        # Launch execution
        returncode = cmd_wrapper.CmdWrapper(
            cmd, out_log, err_log, self.global_log).launch()

        # create zipfile and wirte output inside
        zf = zipfile.ZipFile(
            Path(self.io_dict["out"]["output_zip_path"]),
            "w")
        for curves_outfile in Path(self.tmp_folder).glob("curves_output*"):
            zf.write(
                curves_outfile,
                arcname=curves_outfile.name)
        zf.close()

        # Remove temporary file(s)
        if self.remove_tmp:
            fu.rm(self.tmp_folder)
            fu.log('Removed: %s' % str(self.tmp_folder), out_log)

        return returncode


def curves(input_struc_path: str, input_top_path: str, output_zip_path: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`Curves <biobb_dna.curvesplus.curves.Curves>` class and
    execute the :meth:`launch() <biobb_dna.curvesplus.curves.Curves.launch>` method."""

    return Curves(
        input_struc_path=input_struc_path,
        input_top_path=input_top_path,
        output_zip_path=output_zip_path,
        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Description for the template module.',
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_struc_path', required=True,
                               help='Trajectory or PDB input file. Accepted formats: trj, pdb.')
    parser.add_argument('--input_top_path', required=False,
                        help='Topology file, needed along with .trj file (optional). Accepted formats: top.')
    required_args.add_argument('--output_zip_path', required=True,
                               help='Filename to give to output .lis files (without the .lis extension). Accepted formats: str.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    curves(
        input_struc_path=args.input_struc_path,
        input_top_path=args.input_top_path,
        output_zip_path=args.output_zip_path,
        properties=properties)


if __name__ == '__main__':
    main()
