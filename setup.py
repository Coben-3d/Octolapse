# coding=utf-8
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import platform

# Import version utilities
try:
    from octoprint_octolapse_setuptools import NumberedVersion
    import versioneer
except ImportError:
    print("Warning: Could not import versioning tools")
    class NumberedVersion:
        CurrentVersion = "0.4.5"
        @staticmethod
        def clean_version(v):
            return v
    class versioneer:
        @staticmethod
        def get_versions(verbose=False):
            return {"version": "0.4.5", "full-revisionid": "0000000"}
        @staticmethod
        def get_cmdclass():
            return {}

########################################################################################################################
# The plugin's identifier, has to be unique
plugin_identifier = "octolapse"
plugin_package = "octoprint_octolapse"
plugin_name = "Octolapse"
fallback_version = NumberedVersion.clean_version(NumberedVersion.CurrentVersion)
plugin_version = NumberedVersion.clean_version(versioneer.get_versions(verbose=True)["version"])

if plugin_version == "0+unknown":
    plugin_version = fallback_version
    try:
        plugin_version += "+u." + versioneer.get_versions()['full-revisionid'][0:7]
    except:
        pass

plugin_cmdclass = versioneer.get_cmdclass()
plugin_description = """Create stabilized timelapses of your 3d prints. Highly customizable, loads of presets, lots of fun."""
plugin_author = "Brad Hochgesang"
plugin_author_email = "FormerLurker@pm.me"
plugin_url = "https://github.com/FormerLurker/Octolapse"
plugin_license = "AGPLv3"

plugin_requires = [
    "pillow>=9.3,<11",
    "sarge>=0.1.5",
    "six",
    "OctoPrint>=1.4.0",
    "psutil",
    "file_read_backwards",
    "setuptools>=6.0",
    "awesome-slugify>=1.6.5,<1.7"
]

plugin_additional_data = [
    'data/*.json',
    'data/images/*.png',
    'data/images/*.jpeg',
    'data/lib/c/*.cpp',
    'data/lib/c/*.h',
    'data/webcam_types/*',
    'data/fonts/*'
]

plugin_additional_packages = ['octoprint_octolapse_setuptools']
plugin_ignored_packages = []

########################################################################################################################
# C++ Extension compiler options - Python 3.11+ compatible version
########################################################################################################################

DEBUG = False

def get_compiler_opts(compiler_type):
    """Get compiler options based on compiler type string"""
    
    if DEBUG:
        if compiler_type == 'msvc':
            return {
                'extra_compile_args': ['/EHsc', '/Z7'],
                'extra_link_args': ['/DEBUG'],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }
        elif compiler_type in ['unix', 'cygwin', 'mingw32']:
            return {
                'extra_compile_args': ['-g'],
                'extra_link_args': ['-g'],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }
        else:
            return {
                'extra_compile_args': [],
                'extra_link_args': [],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }
    else:
        if compiler_type == 'msvc':
            return {
                'extra_compile_args': ['/O2', '/fp:fast', '/GL', '/analyze', '/Gy', '/MD', '/EHsc'],
                'extra_link_args': [],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }
        elif compiler_type in ['unix', 'cygwin', 'mingw32']:
            return {
                'extra_compile_args': ['-O3', '-std=c++11'],
                'extra_link_args': [],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }
        else:
            return {
                'extra_compile_args': ['-O3', '-std=c++11'],
                'extra_link_args': [],
                'define_macros': [('IS_PYTHON_EXTENSION', '1')]
            }


class build_ext_subclass(build_ext):
    def build_extensions(self):
        print("Compiling Octolapse Parser Extension with {0}.".format(self.compiler.compiler_type))
        
        opts = get_compiler_opts(self.compiler.compiler_type)
        
        for extension in self.extensions:
            for attrib, value in opts.items():
                getattr(extension, attrib).extend(value)
        
        build_ext.build_extensions(self)
        
        for extension in self.extensions:
            print(f"Build Extensions for {extension.name} - extra_compile_args: {extension.extra_compile_args} - extra_link_args: {extension.extra_link_args} - define_macros: {extension.define_macros}")

plugin_ext_sources = [
    'octoprint_octolapse/data/lib/c/gcode_position_processor.cpp',
    'octoprint_octolapse/data/lib/c/gcode_parser.cpp',
    'octoprint_octolapse/data/lib/c/gcode_position.cpp',
    'octoprint_octolapse/data/lib/c/parsed_command.cpp',
    'octoprint_octolapse/data/lib/c/parsed_command_parameter.cpp',
    'octoprint_octolapse/data/lib/c/position.cpp',
    'octoprint_octolapse/data/lib/c/python_helpers.cpp',
    'octoprint_octolapse/data/lib/c/snapshot_plan.cpp',
    'octoprint_octolapse/data/lib/c/snapshot_plan_step.cpp',
    'octoprint_octolapse/data/lib/c/stabilization.cpp',
    'octoprint_octolapse/data/lib/c/stabilization_results.cpp',
    'octoprint_octolapse/data/lib/c/stabilization_smart_layer.cpp',
    'octoprint_octolapse/data/lib/c/stabilization_smart_gcode.cpp',
    'octoprint_octolapse/data/lib/c/logging.cpp',
    'octoprint_octolapse/data/lib/c/utilities.cpp',
    'octoprint_octolapse/data/lib/c/trigger_position.cpp',
    'octoprint_octolapse/data/lib/c/gcode_comment_processor.cpp',
    'octoprint_octolapse/data/lib/c/extruder.cpp'
]

cpp_gcode_parser = Extension(
    'GcodePositionProcessor',
    sources=plugin_ext_sources,
    language="c++"
)

additional_setup_parameters = {
    "ext_modules": [cpp_gcode_parser],
    "cmdclass": {"build_ext": build_ext_subclass}
}

try:
    import octoprint_setuptools
except ImportError:
    print("Could not import OctoPrint's setuptools, are you sure you are running under the correct Python environment?")
    sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=plugin_ignored_packages,
    additional_data=plugin_additional_data,
    cmdclass=plugin_cmdclass
)

if len(additional_setup_parameters):
    from octoprint.util import dict_merge
    setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

setup(**setup_parameters)
