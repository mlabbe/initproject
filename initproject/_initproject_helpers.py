#
# _initproject_helpers.py
#

import os
import jinja2
import shutil
import os.path

class GeneratorError(Exception):
    """Exception raised by generator module.

    Attributes:
       self.message -- description of what happened"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

    

def mkdir(path):
    """mkdir only if needed"""
    try: 
        os.mkdir(path)
    except FileExistsError:
        pass


def which_all(path_programs):
    """confirm all programs in iterable path_programs are in the path.
    Returns list of missing program error messages."""
    missing_programs = []
    for program in path_programs:
        if not shutil.which(program):
            missing_programs.append("%s was not found in PATH." % program)
    return missing_programs

def load_tmpl(module, name, cfg):
    """load a template, or fallback to the hardcoded one if it's not found
    in cwd.   Return the rendererd template, with cfg as the arguments."""
    tmpl_file = "%s.tmpl" % name
    if os.path.isfile(tmpl_file):
        # load jinja2 template
        with open(tmpl_file, "r") as f:
            tmpl_str = f.read()
    else:
        tmpl_str = _call(module, "tmpl_%s" % name)

    tmpl = jinja2.Template(tmpl_str, trim_blocks=True)
    return tmpl.render(cfg)

def render_tmpl(tmpl_str, cfg):
    tmpl = jinja2.Template(tmpl_str, trim_blocks=True)
    return tmpl.render(cfg)


def write(out_path, contents):
    with open(out_path, "w") as f:
        f.write(contents)


def _call(module, func_str):
    func = getattr(module, func_str)
    return func()


licenses = {'mit':
"""The MIT License (MIT)

Copyright (c) {{ copyright_years }} {{ copyright_holder }}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
}
