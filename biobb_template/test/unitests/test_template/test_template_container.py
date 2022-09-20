from biobb_common.tools import test_fixtures as fx
from biobb_template.template.template_container import template_container

class TestTemplateDocker():
    def setup_class(self):
        fx.test_setup(self, 'template_container')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_template_docker(self):
        returncode= template_container(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_file_path'])
        assert fx.equal(self.paths['output_file_path'], self.paths['ref_output_file_path'])
        assert fx.exe_success(returncode)

class TestTemplateSingularity():
    def setup_class(self):
        fx.test_setup(self, 'template_singularity')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_template_singularity(self):
        returncode= template_container(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_file_path'])
        assert fx.equal(self.paths['output_file_path'], self.paths['ref_output_file_path'])
        assert fx.exe_success(returncode)
