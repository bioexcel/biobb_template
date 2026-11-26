#!/usr/bin/env python3

"""Module containing the TemplateContainer class and the command line interface."""
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu


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
            * **binary_path** (*str*) - ("zip") Example of executable binary property.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None) Container path definition.
            * **container_image** (*str*) - ('mmbirb/zip:latest') Container image definition.
            * **container_volume_path** (*str*) - ('/tmp') Container volume path definition.
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
    def __init__(self, input_file_path1: str, output_file_path: str, input_file_path2: str | None = None, properties: dict | None = None, **kwargs) -> None:
        # 3. BiobbObject builds self.io_dict from the arguments documented in the docstring and sets one
        # attribute per documented property (ie: self.boolean_property) with the default of the docstring.
        # Add after this call only what is specific to the block (ie: values computed from the properties)
        super().__init__(**locals())

    def run(self) -> None:
        """Execute the :class:`TemplateContainer <template.template_container.TemplateContainer>` object."""

        # 4. BiobbObject.launch() has already checked the restart property and staged the files
        # in the sandbox before calling run(). The command runs in the sandbox (the container volume
        # in containers) and uses the staged files by name, from self.stage_io_dict

        # 5. Prepare the command line parameters as instructions list
        instructions = ['-j']
        if self.boolean_property:
            instructions.append('-v')
            fu.log('Appending optional boolean property', self.out_log, self.global_log)

        # 6. Build the actual command line as a list of items (elements order will be maintained)
        self.cmd = [self.binary_path,
                    ' '.join(instructions),
                    self.stage_io_dict['out']['output_file_path'],
                    self.stage_io_dict['in']['input_file_path1']]
        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 7. Repeat for optional input files if provided
        if self.stage_io_dict['in'].get('input_file_path2'):
            # Append optional input_file_path2 to cmd
            self.cmd.append(self.stage_io_dict['in']['input_file_path2'])
            fu.log('Appending optional argument to command line', self.out_log, self.global_log)

        # 8. Uncomment to check the command line
        # print(' '.join(cmd))

        # Run Biobb block
        self.run_biobb()

        # 9. After run(), BiobbObject.launch() copies the outputs from the sandbox to the host,
        # removes the temporary files (self.tmp_files, ie: the folders of self.create_tmp_dir())
        # and checks the outputs. Python code that reads or writes the files of the sandbox uses
        # self.sandbox_file(<argument>), and self.staged_path(<host path>) gives the path the command
        # uses for a file created in the sandbox (ie: by self.create_tmp_file())


# 10. Name the launcher function as the module: it gets the arguments and the docstring of the class.
# The command line is TemplateContainer.main(), console script '<module>:TemplateContainer.main' in setup.py
template_container = launcher(TemplateContainer)


if __name__ == '__main__':
    TemplateContainer.main()

# 13. Complete documentation strings
