#
# nativeproject.py
#

"""
Refresh a project that complies with the Frogtoss Native Project Standards.

http://www.frogtoss.com/labs/pages/native-project-standards.html
"""

from os.path import join as pjoin
from _initproject_helpers import mkdir
import _initproject_helpers as help

def describe_short():
    return """Frogtoss Native Project Standards-compliant project"""


def validate_env():
    missing_program_errors = help.which_all(('premake5',))
    return missing_program_errors


def refresh():
    paths = cfg['supported_paths']
    src = paths['src']
    
    if src['enable']:
        mkdir(pjoin(out_path, 'src'))
        if src['shaders']:
            mkdir(pjoin(out_path, 'src', 'shaders'))
        if src['config']:
            mkdir(pjoin(out_path, 'src', 'config'))
            # todo: generate config

    if paths['public_include']:
        mkdir(pjoin(out_path, 'include'))

    if paths['build']:
        mkdir(pjoin(out_path, 'build'))

    if paths['vendors']:
        mkdir(pjoin(out_path, 'vendors'))

    if paths['test']:
        mkdir(pjoin(out_path, 'test'))

    # generate readme
    help.write(pjoin(out_path, 'README.md'),
               help.load_tmpl(module, 'readme', cfg))

    # generate license
    share = cfg['share']
    if share['enable']:
        if not share['license'] in help.licenses:
            raise help.GenerateError("Invalid license type")

        license_str = help.licenses[share['license']]
        help.write(pjoin(out_path, 'LICENSE'),
                   help.render_tmpl(license_str, cfg))
        
#
# Fallback templates
#
        
def tmpl_readme():
    return """# {{ name }} #

## Supported Environments ##
{% for arch in supported_environments %}
 - {{ arch }}
{% endfor %}

# Contact #
{{ author }} can be reached at {{ email }} or on Twitter at @{{ twitter }}.
"""
