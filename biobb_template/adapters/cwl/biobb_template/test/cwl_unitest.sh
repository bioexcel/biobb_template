#!/usr/bin/env bash

RUNNER=cwltool

BIOBB_TEMPLATE=$HOME/projects/BioBB/biobb_template/biobb_template/cwl/biobb_template
cwltool $BIOBB_TEMPLATE/template/template.cwl $BIOBB_TEMPLATE/test/template/template.yml