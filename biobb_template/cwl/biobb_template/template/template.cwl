#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: template
hints:
  DockerRequirement:
    dockerPull: biobb_template/biobb_template:latest
inputs:
  input_file_path1:
    type: File
    inputBinding:
      position: 1
      prefix: --input_file_path1

  input_file_path2:
    type: File?
    inputBinding:
      position: 2
      prefix: --input_file_path2

  output_file_path:
    type: string
    inputBinding:
      position: 3
      prefix: --output_file_path
    default: "output.zip"

  config:
    type: string?
    inputBinding:
      position: 4
      prefix: --config

outputs:
  output_file_path:
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)

$namespaces:
  edam: http://edamontology.org/
$schemas:
  - http://edamontology.org/EDAM_1.22.owl
