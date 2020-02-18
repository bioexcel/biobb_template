import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_template.template import template

@task(input_file_path1=FILE_IN, input_file_path2=FILE_IN, output_file_path=FILE_OUT)
def template_pc(input_file_path1, input_file_path2, output_file_path, properties, **kwargs):
    try:
        template.Template(input_file_path1=input_file_path1, input_file_path2=input_file_path2, output_file_path=output_file_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_file_path)

