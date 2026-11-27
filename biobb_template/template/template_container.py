#!/usr/bin/env python3

"""Module containing the TemplateContainer class and the command line interface."""
from biobb_common.generic.biobb_object import launcher
from biobb_template.template.template import Template


# Any block runs in a container (Docker, Singularity, pcocc) with the container properties of BiobbObject:
# it needs no code for it. This block is the Template block with the container properties documented in
# its docstring, which adds them to the JSON schemas and the docs. Document them in the docstring of your
# block (see template.py for the rest of the block) when its tool is available in a container image
class TemplateContainer(Template):
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
            * **container_path** (*str*) - (None) Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container: the sandbox is mounted there and the command runs in it.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash -c") Path to the binary executable of the container shell.

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


# The launcher function and the command line, as in template.py
template_container = launcher(TemplateContainer)


if __name__ == '__main__':
    TemplateContainer.main()
