#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Short description for the template module in Restructured Text (reST) syntax.
  Mandatory.

doc: |-
  Long description for the template module in Restructured Text (reST) syntax. Optional.

baseCommand: template

hints:
  DockerRequirement:
    dockerPull: ''

inputs:
  input_file_path1:
    label: Description for the first input file path
    doc: |-
      Description for the first input file path
      Type: string
      File type: input
      Accepted formats: top
      Example file: https://urlto.sample
    type: File
    format:
    - edam:format_3881
    inputBinding:
      position: 1
      prefix: --input_file_path1

  output_file_path:
    label: Description for the output file path
    doc: |-
      Description for the output file path
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://urlto.sample
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.zip

  input_file_path2:
    label: Description for the second input file path (optional)
    doc: |-
      Description for the second input file path (optional)
      Type: string
      File type: input
      Accepted formats: dcd
      Example file: https://urlto.sample
    type: File?
    format:
    - edam:format_3878
    inputBinding:
      prefix: --input_file_path2

  config:
    label: Advanced configuration options for biobb_template Template
    doc: |-
      Advanced configuration options for biobb_template Template. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_template Template documentation: https://biobb-template.readthedocs.io/en/latest/template.html#module-template.template
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: Description for the output file path
    doc: |-
      Description for the output file path
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_3987

$namespaces:
  edam: http://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
