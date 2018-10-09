from pycompss.api.task import task
from biobb_common.tools import file_utils as fu
from template import template

@task(input_file_path=FILE_IN, output_file_path=FILE_OUT)
def template_pc(input_file_path, output_file_path, properties, **kwargs):
    try:
        template.Template(input_file_path=input_file_path, output_file_path=output_file_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_file_path)
