#!/usr/bin/env python3

"""Module containing the TemplateContainer class and the command line interface."""
import argparse
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


# 1. Rename class as required
class TemplateContainer(BiobbObject):
    """
    | biobb_template TemplateContainer
    | Short description for the `template container <http://templatedocumentation.org>`_ module in Restructured Text (reST) syntax. Mandatory.
    | Long description for the `template container <http://templatedocumentation.org>`_ module in Restructured Text (reST) syntax. Optional.

    Args:
        input_file_path1 (str): Description for the first input file path. File type: input. `Sample file <https://urlto.sample>`_. Accepted formats: top (edam:format_3881).
        input_file_path2 (str) (Optional): Description for the second input file path (optional). File type: input. `Sample file <https://urlto.sample>`_. Accepted formats: dcd (edam:format_3878).
        output_file_path (str): Description for the output file path. File type: output. `Sample file <https://urlto.sample>`_. Accepted formats: zip (edam:format_3987).
        properties (dic):
            * **boolean_property** (*bool*) - (True) Example of boolean property.
            * **executable_binary_property** (*str*) - ("zip") Example of executable binary property.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*str*) - (None) Container path definition.
            * **container_image** (*str*) - ('mmbirb/zip:latest') Container image definition.
            * **container_volume_path** (*str*) - ('/tmp') Container volume path definition.
            * **container_working_dir** (*str*) - (None) Container working directory definition.
            * **container_user_id** (*str*) - (None) Container user_id definition.
            * **container_shell_path** (*str*) - ('/bin/bash') Path to default shell inside the container.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_template.template.template_container import template_container

            prop = { 
                'boolean_property': True,
                'container_path': 'docker',
                'container_image': 'mmbirb/zip:latest',
                'container_volume_path': '/tmp'
            }
            template_container(input_file_path1='/path/to/myTopology.top',
                            output_file_path='/path/to/newCompressedFile.zip',
                            input_file_path2='/path/to/mytrajectory.dcd',
                            properties=prop)

    Info:
        * wrapped_software:
            * name: Zip
            * version: >=3.0
            * license: BSD 3-Clause
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # 2. Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_file_path1, output_file_path, 
                input_file_path2 = None, properties = None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = { 
            'in': { 'input_file_path1': input_file_path1, 'input_file_path2': input_file_path2 }, 
            'out': { 'output_file_path': output_file_path } 
        }

        # 3. Include all relevant properties here as 
        # self.property_name = properties.get('property_name', property_default_value)

        # Properties specific for BB
        self.boolean_property = properties.get('boolean_property', True)
        self.executable_binary_property = properties.get('executable_binary_property', 'zip')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`TemplateContainer <template.template_container.TemplateContainer>` object."""
        
        # 4. Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, self.out_log)

        # 5. Prepare the command line parameters as instructions list
        instructions = ['-j']
        if self.boolean_property:
            instructions.append('-v')
            fu.log('Appending optional boolean property', self.out_log, self.global_log)

        # 6. Build the actual command line as a list of items (elements order will be maintained)
        self.cmd = [self.executable_binary_property,
               ' '.join(instructions), 
               self.stage_io_dict['out']['output_file_path'],
               self.stage_io_dict['in']['input_file_path1']]
        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 7. Repeat for optional input files if provided
        if self.stage_io_dict['in']['input_file_path2']:
            # Append optional input_file_path2 to cmd
            self.cmd.append(self.stage_io_dict['in']['input_file_path2'])
            fu.log('Appending optional argument to command line', self.out_log, self.global_log)

        # 8. Uncomment to check the command line 
        # print(' '.join(cmd))

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporary file(s)
        if self.remove_tmp and self.stage_io_dict["unique_dir"]:
            self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
            self.remove_tmp_files()

        return self.return_code

def template_container(input_file_path1: str, output_file_path: str, input_file_path2: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`TemplateContainer <template.template_container.TemplateContainer>` class and
    execute the :meth:`launch() <template.template_container.TemplateContainer.launch>` method."""

    return TemplateContainer(input_file_path1=input_file_path1, 
                            output_file_path=output_file_path,
                            input_file_path2=input_file_path2,
                            properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='Description for the template container module.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # 10. Include specific args of each building block following the examples. They should match step 2
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_file_path1', required=True, help='Description for the first input file path. Accepted formats: top.')
    parser.add_argument('--input_file_path2', required=False, help='Description for the second input file path (optional). Accepted formats: dcd.')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: zip.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # 11. Adapt to match Class constructor (step 2)
    # Specific call of each building block
    template_container(input_file_path1=args.input_file_path1, 
                      output_file_path=args.output_file_path, 
                      input_file_path2=args.input_file_path2, 
                      properties=properties)

if __name__ == '__main__':
    main()

# 13. Complete documentation strings