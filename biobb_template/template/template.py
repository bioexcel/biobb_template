#!/usr/bin/env python3

"""Module containing the Template class and the command line interface."""
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu


# 1. Rename class as required
# 2. Complete the docstring: BiobbObject reads the arguments and the properties from it (the defaults are
# Python literals, ie: ("zip"), (True), (None)), and the JSON schemas, the docs and the command line help are
# generated from it
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

    # Optional: short flags of the command line. By default only a block with one input argument gets -i
    # and only a block with one output argument gets -o
    # custom_flags = {'input_file_path1': '-t'}

    # 3. Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, input_file_path1: str, output_file_path: str, input_file_path2: str | None = None, properties: dict | None = None, **kwargs) -> None:
        # 4. BiobbObject builds self.io_dict from the arguments documented in the docstring and sets one
        # attribute per documented property (ie: self.boolean_property) with the default of the docstring.
        # Add after this call only what is specific to the block (ie: values computed from the properties)
        super().__init__(**locals())

    # Optional: define prepare(self) to check the values of the properties (BiobbObject already checks that
    # the input files and the folders of the output files exist) or to create files that are staged with the
    # inputs (add them to self.io_dict['in']). BiobbObject.launch() calls it before staging the files

    def run(self) -> None:
        """Execute the :class:`Template <template.template.Template>` object."""

        # 5. BiobbObject.launch() has already checked the restart property, called prepare() and staged the
        # files in the sandbox before calling run(). The command runs in the sandbox (the container volume
        # in containers) and uses the staged files by name, from self.stage_io_dict

        # 6. Prepare the command line parameters as instructions list
        instructions = ['-j']
        if self.boolean_property:
            instructions.append('-v')
            fu.log('Appending optional boolean property', self.out_log, self.global_log)

        # 7. Build the actual command line as a list of items, one per argument (elements order will be maintained)
        self.cmd = [self.binary_path,
                    *instructions,
                    self.stage_io_dict['out']['output_file_path'],
                    self.stage_io_dict['in']['input_file_path1']]
        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 8. Repeat for optional input files if provided
        if self.stage_io_dict['in'].get('input_file_path2'):
            # Append optional input_file_path2 to cmd
            self.cmd.append(self.stage_io_dict['in']['input_file_path2'])
            fu.log('Appending optional argument to command line', self.out_log, self.global_log)

        # 9. Run the command: run_biobb() writes it in the log and sets self.return_code to its exit code
        self.run_biobb()

        # 10. After run(), BiobbObject.launch() copies the outputs from the sandbox to the host,
        # removes the temporary files (self.tmp_files, ie: the folders of self.create_tmp_dir())
        # and checks the outputs. Python code that reads or writes the files of the sandbox uses
        # self.sandbox_file(<argument>), and self.staged_path(<host path>) gives the path the command
        # uses for a file created in the sandbox (ie: by self.create_tmp_file())


# 11. Name the launcher function as the module: it gets the arguments and the docstring of the class.
# The command line is Template.main(), console script '<module>:Template.main' in setup.py
template = launcher(Template)


if __name__ == '__main__':
    Template.main()
