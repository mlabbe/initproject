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

    if paths['public_include']:
        mkdir(pjoin(out_path, 'include'))

    if paths['build']:
        mkdir(pjoin(out_path, 'build'))

    if paths['vendors']:
        mkdir(pjoin(out_path, 'vendors'))
        mkdir(pjoin(out_path, 'vendors', 'include'))
        mkdir(pjoin(out_path, 'vendors', 'lib'))

    if paths['test']:
        mkdir(pjoin(out_path, 'test'))

    # generate readme
    help.write(pjoin(out_path, 'README.md'),
               help.load_tmpl(module, 'README_md', cfg))

    # generate license
    share = cfg['share']
    if share['enable']:
        if not share['license'] in help.licenses:
            raise help.GenerateError("Invalid license type")

        license_str = help.licenses[share['license']]
        help.write(pjoin(out_path, 'LICENSE'),
                   help.render_tmpl(license_str, cfg))


    # generate config
    if paths['src']['config']:
        config_filename = '%sconfig.h' % cfg['prefix']
        help.write(pjoin(out_path, 'src', 'config', config_filename),
                   help.load_tmpl(module, 'config_h', cfg))
        
#
# Fallback templates
#
        
def tmpl_README_md():
    return """# {{ name }} #

{% if project_type == "lib" or project_type == "dll" %}
# Example Usage

```C
#include <{{ prefix }}.h>
```
{% endif %}

## Changelog ##

release | what's new                          | date
--------|-------------------------------------|---------
0.0.1   | initial                             | 

## Building ##

{% if supported_paths.build %}
{{ name }} uses [Premake5](https://premake.github.io/download.html) generated Makefiles and IDE project files.  The generated project files are checked in under `build/` so you don't have to download and use Premake in most cases.
{% endif %}

# Copyright and Credit #

Copyright &copy; {{ copyright_years }} {{ copyright_holder }}. {% if share.enable %}File [LICENSE](LICENSE) covers all files in this repo unless expressly noted.{% endif %}

{{ name }} by {{ author_name }}
<{{ author_email }}> 
{% if author_twitter %}[@{{ author_twitter }}](https://www.twitter.com/{{ author_twitter }}) {% endif %}

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact author]({{ author_contact_url }})
"""

def tmpl_config_h():
    return"""/* 
 * {{ name }} Copyright (C) {{ copyright_years }} {{ copyright_holder }}
 */

#pragma once

{% for etype in execution_types %}
//
// {{ etype|title }}
//
#if defined({{ etype|upper }})
#endif
{% endfor %}
"""
