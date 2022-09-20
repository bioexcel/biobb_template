# BioBB TEMPLATE Command Line Help
Generic usage:
```python
biobb_command [-h] --config CONFIG --input_file(s) <input_file(s)> --output_file <output_file>
```
-----------------


## Template_container
Short description for the template container module in Restructured Text (reST) syntax. Mandatory.
### Get help
Command:
```python
template_container -h
```
    usage: template_container [-h] [--config CONFIG] --input_file_path1 INPUT_FILE_PATH1 [--input_file_path2 INPUT_FILE_PATH2] --output_file_path OUTPUT_FILE_PATH
    
    Description for the template container module.
    
    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       Configuration file
      --input_file_path2 INPUT_FILE_PATH2
                            Description for the second input file path (optional). Accepted formats: dcd.
    
    required arguments:
      --input_file_path1 INPUT_FILE_PATH1
                            Description for the first input file path. Accepted formats: top.
      --output_file_path OUTPUT_FILE_PATH
                            Description for the output file path. Accepted formats: zip.
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_file_path1** (*string*): Description for the first input file path. File type: input. [Sample file](https://urlto.sample). Accepted formats: TOP
* **input_file_path2** (*string*): Description for the second input file path (optional). File type: input. [Sample file](https://urlto.sample). Accepted formats: DCD
* **output_file_path** (*string*): Description for the output file path. File type: output. [Sample file](https://urlto.sample). Accepted formats: ZIP
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **boolean_property** (*boolean*): (True) Example of boolean property..
* **binary_path** (*string*): (zip) Example of executable binary property..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
* **container_path** (*string*): (None) Container path definition..
* **container_image** (*string*): (mmbirb/zip:latest) Container image definition..
* **container_volume_path** (*string*): (/tmp) Container volume path definition..
* **container_working_dir** (*string*): (None) Container working directory definition..
* **container_user_id** (*string*): (None) Container user_id definition..
* **container_shell_path** (*string*): (/bin/bash) Path to default shell inside the container..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template_container.yml)
```python
properties:
  boolean_property: false
  container_image: mmbirb/zip:latest
  container_path: docker
  container_volume_path: /tmp
  remove_tmp: true

```
#### Command line
```python
template_container --config config_template_container.yml --input_file_path1 urlto.sample --input_file_path2 urlto.sample --output_file_path urlto.sample
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template_container.json)
```python
{
  "properties": {
    "boolean_property": false,
    "remove_tmp": true,
    "container_path": "docker",
    "container_image": "mmbirb/zip:latest",
    "container_volume_path": "/tmp"
  }
}
```
#### Command line
```python
template_container --config config_template_container.json --input_file_path1 urlto.sample --input_file_path2 urlto.sample --output_file_path urlto.sample
```

## Template
Short description for the template module in Restructured Text (reST) syntax. Mandatory.
### Get help
Command:
```python
template -h
```
    usage: template [-h] [--config CONFIG] --input_file_path1 INPUT_FILE_PATH1 [--input_file_path2 INPUT_FILE_PATH2] --output_file_path OUTPUT_FILE_PATH
    
    Description for the template module.
    
    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       Configuration file
      --input_file_path2 INPUT_FILE_PATH2
                            Description for the second input file path (optional). Accepted formats: dcd.
    
    required arguments:
      --input_file_path1 INPUT_FILE_PATH1
                            Description for the first input file path. Accepted formats: top.
      --output_file_path OUTPUT_FILE_PATH
                            Description for the output file path. Accepted formats: zip.
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_file_path1** (*string*): Description for the first input file path. File type: input. [Sample file](https://urlto.sample). Accepted formats: TOP
* **input_file_path2** (*string*): Description for the second input file path (optional). File type: input. [Sample file](https://urlto.sample). Accepted formats: DCD
* **output_file_path** (*string*): Description for the output file path. File type: output. [Sample file](https://urlto.sample). Accepted formats: ZIP
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **boolean_property** (*boolean*): (True) Example of boolean property..
* **binary_path** (*string*): (zip) Example of executable binary property..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template.yml)
```python
properties:
  boolean_property: false
  remove_tmp: true

```
#### [Singularity config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template_singularity.yml)
```python
properties:
  boolean_property: false
  container_image: bioexcel-zip_container-master-latest.simg
  container_path: singularity
  container_volume_path: /tmp
  binary_path: /opt/conda/bin/zip
  remove_tmp: false

```
#### Command line
```python
template --config config_template.yml --input_file_path1 urlto.sample --input_file_path2 urlto.sample --output_file_path urlto.sample
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template.json)
```python
{
  "properties": {
    "boolean_property": false,
    "remove_tmp": true
  }
}
```
#### [Singularity config file](https://github.com/bioexcel/biobb_template/blob/master/biobb_template/test/data/config/config_template_singularity.json)
```python
{
  "properties": {
    "boolean_property": false,
    "remove_tmp": false,
    "binary_path": "/opt/conda/bin/zip",
    "container_path": "singularity",
    "container_image": "bioexcel-zip_container-master-latest.simg",
    "container_volume_path": "/tmp"
  }
}
```
#### Command line
```python
template --config config_template.json --input_file_path1 urlto.sample --input_file_path2 urlto.sample --output_file_path urlto.sample
```
