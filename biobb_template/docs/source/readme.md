[![](https://img.shields.io/github/v/tag/bioexcel/biobb_template?label=Version)](https://GitHub.com/bioexcel/biobb_template/tags/)

[![](https://img.shields.io/badge/OS-Unix%20%7C%20MacOS-blue)](https://github.com/bioexcel/biobb_template)
[![](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![](https://img.shields.io/badge/Open%20Source%3f-Yes!-blue)](https://github.com/bioexcel/biobb_template)

[![](https://readthedocs.org/projects/biobb-template/badge/?version=latest&label=Docs)](https://biobb-template.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/website?down_message=Offline&label=Biobb%20Website&up_message=Online&url=https%3A%2F%2Fmmb.irbbarcelona.org%2Fbiobb%2F)](https://mmb.irbbarcelona.org/biobb/)
[![](https://img.shields.io/badge/Youtube-tutorials-blue?logo=youtube&logoColor=red)](https://www.youtube.com/@BioExcelCoE/search?query=biobb)
[![](https://zenodo.org/badge/DOI/10.1038/s41597-019-0177-4.svg)](https://doi.org/10.1038/s41597-019-0177-4)
[![](https://img.shields.io/endpoint?color=brightgreen&url=https%3A%2F%2Fapi.juleskreuer.eu%2Fcitation-badge.php%3Fshield%26doi%3D10.1038%2Fs41597-019-0177-4)](https://www.nature.com/articles/s41597-019-0177-4#citeas)

[![](https://docs.bioexcel.eu/biobb_template/junit/testsbadge.svg)](https://docs.bioexcel.eu/biobb_template/junit/report.html)
[![](https://docs.bioexcel.eu/biobb_template/coverage/coveragebadge.svg)](https://docs.bioexcel.eu/biobb_template/coverage/)
[![](https://docs.bioexcel.eu/biobb_template/flake8/flake8badge.svg)](https://docs.bioexcel.eu/biobb_template/flake8/)
[![](https://img.shields.io/github/last-commit/bioexcel/biobb_template?label=Last%20Commit)](https://github.com/bioexcel/biobb_template/commits/master)
[![](https://img.shields.io/github/issues/bioexcel/biobb_template.svg?color=brightgreen&label=Issues)](https://GitHub.com/bioexcel/biobb_template/issues/)


# biobb_template

## Introduction
Biobb_template is a complete code template to promote and facilitate the creation of
new Biobbs by the community.
Biobb (BioExcel building blocks) packages are Python building blocks that
create new layer of compatibility and interoperability over popular
bioinformatics tools.
The latest documentation of this package can be found in our readthedocs site:
[latest API documentation](http://biobb-template.readthedocs.io/en/latest/).

## Version
v4.1.0 2023.4

## Installation

If you have no experience with anaconda, please first take a look to the [New with anaconda?](https://biobb-documentation.readthedocs.io/en/latest/first_steps.html#new-with-anaconda) section of the [official documentation](https://biobb-documentation.readthedocs.io/en/latest/).

### Download repository

Although the biobb_template repository is available at GitHub and thus you can clone it, we strongly recommend you to [**download it compressed**](https://github.com/bioexcel/biobb_template/archive/master.zip) and start your new project from scratch. 

### Create new conda environment

Once you have the project unzipped in your computer, please follow the next steps to create a new conda environment:

```console
cd biobb_template-master
conda env create -f conda_env/environment.yml
```

### Update environment paths

Edit **conda_env/biobb_template.pth** with the paths to your *biobb_template* folder. Example:

```console
/home/user_name/projects/biobb_template/
/home/user_name/projects/biobb_template/biobb_template/biobb_template
```

Copy the edited **conda_env/biobb_template.pth** file to the site-packages folder of your environment. This folder is in */[anaconda-path]/envs/biobb_template/lib/python3.7/site-packages*, where */[anaconda-path]* is usually */anaconda3* or */opt/conda*.

```console
cp conda_env/biobb_template.pth /[anaconda-path]/envs/biobb_template/lib/python3.7/site-packages
```

### Activate environment

Then, activate the recently created *biobb_template* conda environment:

```console
conda activate biobb_template
```

### Create repository

This template includes some folders not standard for a biobb, such as **biobb_template/adapters/**, **biobb_template/notebooks/** or **conda_env/**. For the sake of having a pure biobb structure, you should uncomment the three last lines of the **.gitignore** file before creating a new git repository:

```console
biobb_template/adapters
biobb_template/notebooks
conda_env
```
Then, inialitize repository:

```console
git init
```

### Binary paths configuration

Additionally, it's recommendable to configure binary paths in your environment in order to ease the command line execution. More info about this subject in the [Binary path configuration](https://biobb-documentation.readthedocs.io/en/latest/execution.html#binary-path-configuration) section of the [official documentation](https://biobb-documentation.readthedocs.io/en/latest/).

## Run tests

To run tests, please execute the following instruction:

```console
pytest /path/to/biobb_template/biobb_template/test/unitests/test_template/test_template.py
```
Or, if you prefer to show the BioBB output during the test process:

```console
pytest -s /path/to/biobb_template/biobb_template/test/unitests/test_template/test_template.py
```

## Documentation

[Click here to find the API Documentation example](https://biobb-template.readthedocs.io/en/latest/template.html) for this template and [here for Command Line documentation](http://biobb-template.readthedocs.io/en/latest/command_line.html).

And here you can find [the full documentation](https://biobb-documentation.readthedocs.io/en/latest/) about how to build a new **BioExcel building block** from scratch.

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU Horizon Europe [101093290](https://cordis.europa.eu/project/id/101093290), EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2022 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2022 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
