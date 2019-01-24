#!/usr/bin/env python

"""Module containing the Template class and the command line interface."""
import argparse
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.command_wrapper import cmd_wrapper

class Template(object):
    """Wrapper class for the template (http://templatedocumentation.org) module.

    Args:
        input_file_path (str): Path to the input file.
        output_file_path (str): Path to the output file.
        properties (dic):
            | - **float_property** (*float*) - (1.0) Example of float property.
            | - **string_property** (*str*) - ("foo") Example of string property.
            | - **boolean_property** (*bool*) - (True) Example of boolean property.
            | - **executable_binary_property** (*str*) - ("echo") Example of executable binary property.
    """

    def __init__(self, input_file_path, output_file_path, properties, **kwargs):
        properties = properties or {}

        # Input/Output files
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

        # Properties specific for BB
        self.float_property = properties.get('float_property',1.0)
        self.string_property = properties.get('string_property', 'foo')
        self.boolean_property = properties.get('boolean_property',True)
        self.executable_binary_property = properties.get('booleaexecutable_binary_property','echo')

        # Properties common in all BB
        self.can_write_console_log = properties.get('can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')

    def launch(self):
        """Launches the execution of the template module."""
        out_log, err_log = fu.get_logs(path=self.path, prefix=self.prefix, step=self.step, can_write_console=self.can_write_console_log)

        #Construct command line
        cmd = [self.executable_binary_property,
               '-i', self.input_file_path,
               '-o', self.output_file_path,
               '-f', str(self.float_property),
               '-s', self.string_property]

        if self.boolean_property:
            cmd.append('-b')
            fu.log('Appending optional boolean property', out_log, self.global_log)

        fu.log('Float property: %g' % self.float_property, out_log, self.global_log)
        fu.log('String property: %s' % self.string_property, out_log, self.global_log)

        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()
        tmp_files = ['temp_file1', 'temp_file2']
        removed_files = [f for f in tmp_files if fu.rm(f)]
        fu.log('Removed: %s' % str(removed_files), out_log, self.global_log)
        return returncode

def main():
    parser = argparse.ArgumentParser(description="Wrapper of the template module.")
    parser.add_argument('--config', required=True)
    parser.add_argument('--system', required=False)
    parser.add_argument('--step', required=False)

    #Specific args of each building block
    parser.add_argument('--input_file_path', required=True)
    parser.add_argument('--output_file_path', required=True)

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config, system=args.system).get_prop_dic()
    if args.step:
        properties = properties[args.step]

    #Specific call of each building block
    Template(input_file_path=args.input_file_path, output_gro_path=args.output_file_path, properties=properties).launch()

if __name__ == '__main__':
    main()
