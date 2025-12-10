#!/usr/bin/env python3

"""Module containing the Template class and the command line interface."""
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


# 1. Rename class as required
class Template(BiobbObject):
    """
    | biobb_template Template
    | Short description for the `template <http://templatedocumentation.org>`_ module in Restructured Text (reST) syntax. Mandatory.
    | Long description for the `template <http://templatedocumentation.org>`_ module in Restructured Text (reST) syntax. Optional.

    Args:
        input_file_path1 (str): Description for the first input file path. File type: input. `Sample file <https://urlto.sample>`_. Accepted formats: top (edam:format_3881).
        input_file_path2 (str) (Optional): Description for the second input file path (optional). File type: input. `Sample file <https://urlto.sample>`_. Accepted formats: dcd (edam:format_3878).
        output_file_path (str): Description for the output file path. File type: output. `Sample file <https://urlto.sample>`_. Accepted formats: zip (edam:format_3987).
        properties (dic):
            * **boolean_property** (*bool*) - (True) Example of boolean property.
            * **binary_path** (*str*) - ("zip") Example of executable binary property.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_template.template.template import template

            prop = {
                'boolean_property': True
            }
            template(input_file_path1='/path/to/myTopology.top',
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
    def __init__(self, input_file_path1, output_file_path, input_file_path2=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = {
            'in': {'input_file_path1': input_file_path1, 'input_file_path2': input_file_path2},
            'out': {'output_file_path': output_file_path}
        }

        # 3. Include all relevant properties here as
        # self.property_name = properties.get('property_name', property_default_value)

        # Properties specific for BB
        self.boolean_property = properties.get('boolean_property', True)
        self.binary_path = properties.get('binary_path', 'zip')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        # Check the arguments
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Template <template.template.Template>` object."""

        # 4. Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, self.out_log)

        # 5. Include here all mandatory input files
        # Copy input_file_path1 to temporary folder
        shutil.copy(self.io_dict['in']['input_file_path1'], self.tmp_folder)

        # 6. Prepare the command line parameters as instructions list
        instructions = ['-j']
        if self.boolean_property:
            instructions.append('-v')
            fu.log('Appending optional boolean property', self.out_log, self.global_log)

        # 7. Build the actual command line as a list of items (elements order will be maintained)
        self.cmd = [self.binary_path,
                    ' '.join(instructions),
                    self.io_dict['out']['output_file_path'],
                    str(PurePath(self.tmp_folder).joinpath(PurePath(self.io_dict['in']['input_file_path1']).name))]
        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 8. Repeat for optional input files if provided
        if self.io_dict['in']['input_file_path2']:
            # Copy input_file_path2 to temporary folder
            shutil.copy(self.io_dict['in']['input_file_path2'], self.tmp_folder)
            # Append optional input_file_path2 to cmd
            self.cmd.append(str(PurePath(self.tmp_folder).joinpath(PurePath(self.io_dict['in']['input_file_path2']).name)))
            fu.log('Appending optional argument to command line', self.out_log, self.global_log)

        # 9. Uncomment to check the command line
        # print(' '.join(cmd))

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporary file(s)
        self.tmp_files.append(self.tmp_folder)
        self.remove_tmp_files()

        # Check output arguments
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code


def template(input_file_path1: str, output_file_path: str, input_file_path2: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`Template <template.template.Template>` class and
    execute the :meth:`launch() <template.template.Template.launch>` method."""
    return Template(**dict(locals())).launch()


template.__doc__ = Template.__doc__
main = Template.get_main(template, 'Description for the template module.')


if __name__ == '__main__':
    main()

# 12. Complete documentation strings
