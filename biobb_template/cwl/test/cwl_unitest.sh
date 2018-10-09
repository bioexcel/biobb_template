#!/usr/bin/env bash

BIOBB_TEMPLATE=$HOME/projects/biobb_template/biobb_template
cwltool $BIOBB_TEMPLATE/cwl/template/template.cwl $BIOBB_TEMPLATE/cwl/test/template/template.yml