#
# initproject.py
#

import git
import sys
import glob
import yaml
import shutil
import pkgutil
import os.path
import optparse
import importlib
import execmode.state

import _initproject_helpers as help

from execmode.logging import message, warning, error, fatal_error

VERSION=(0,0,1)

#
# Main module implementation
#


class ProjectTypes:
    """All project types available to generate.
    Iterable with a key, value pair module_name, short_desc"""
    def __init__(self):
        self.modules = {}
        if __name__ == '__main__':
            self.paths = (".")
        else:
            # starting point:
            #http://stackoverflow.com/questions/487971/is-there-a-standard-way-to-list-names-of-python-modules-in-a-package
            fatal_error("sorry, not implemented for installed modules yet.",
                  file=sys.stderr)

    def __iter__(self):
        for path in self.paths:
            wildcard = os.path.join(path, "*.py")
            for python_script in glob.glob(wildcard):
                project_type = os.path.split(python_script)[1]
                if project_type == sys.argv[0]:
                    continue
                project_type = os.path.splitext(project_type)[0]

                module = _init_module(project_type)
                short_desc = _call(module, 'describe_short')
                self.modules[project_type] = short_desc
        return self.modules.items().__iter__()

class RefreshError(Exception):
    """Exception raised for errors during refresh.

    Attributes:
       self.message -- description of what happened"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def parse_yaml_cfg(fstream):
    """parse a yaml config from a stream.  fatal error if parse error.
    yaml.parser.ParserError if a parse resulted in an error.
    """
    return yaml.load(fstream)


def refresh_project(cfg, module, out_path, yaml_config_path=None):
    """refresh/generate a project, using the parsed cfg and module.
    place the result in out_path.

    args:
    cfg - the parsed yaml config

    module - the loaded module

    out_path - the root directory of the project to refresh

    yaml_config_path - the path to the *unparsed* yaml config to copy
    in, or None.


    out_path may already exist, but it it does, it must be a git
    repo with no pending changes. 

    Throw RefreshError if an error occurred.
    """
    # if out_path exists, it must be a git repo with no changes
    if os.path.isdir(out_path):
        try:
            repo = git.Repo(out_path)
        except git.exc.InvalidGitRepositoryError:
            raise RefreshError("%s exists but is not a git repo" % out_path)
        if repo.is_dirty():
            raise RefreshError("%s is a git repo with outstanding changes. " + \
                               "Stash your changes and try again.")
    else:
        help.mkdir(out_path)

    # write cfg back to yaml
    if yaml_config_path:
        out_yml = os.path.join(out_path, ".initproject.yml")
        shutil.copyfile(yaml_config_path, out_yml)

    # share settings with the module
    module.cfg = cfg
    module.out_path = out_path
    module.module = module
    

    # validate module's environment
    errors = _call(module, 'validate_env')
    if len(errors) != 0:
        error_str = '\n'.join(errors)
        raise RefreshError("Error validating environment: " + error_str)
    
    # generate/refresh
    _call(module, 'refresh')

def init_module(module_name):
    """load string module_name, returning module.

    Throws ImportModule if there was a problem."""
    return importlib.import_module(module_name, package=None)

def _call(module, func_str):
    func = getattr(module, func_str)
    return func()

#
# local (non-lib execution)
#

def _list_project_types():
    print("available project types:")

    for name, desc in ProjectTypes():
        print("\t%s\t%s" % (name, desc))
    
    sys.exit(0)

def _print_header():
    print("initproject %d.%d.%d" % VERSION)
    
def _do_args():
    p = optparse.OptionParser()
    p.add_option("-l", "--list-types",
                 action="store_true", dest="list_types",
                 help="list available project types")
    p.add_option("-c", "--config",
                 help="generator config YAML", metavar="YML",
                 dest="config")
    p.add_option("-o", "--out-path",
                 help="output directory", dest="out_path",
                 metavar="OUTPATH")
    p.add_option("-v", "--version", action="store_true",
                 help="version")
                 

    (options, args) = p.parse_args()

    # dispatch acritical execution paths
    if options.list_types:
        _list_project_types()

    if options.config and not options.out_path:
        print("--out-path not specified", file=sys.stderr)
        sys.exit(1)

    # we don't know what to do from here
    if not options.config:
        print("run %s --help for options."% sys.argv[0], file=sys.stderr)
        sys.exit(1)

    return options
        

if __name__ == '__main__':
    # set up debug/release
    execmode.state.set_state(execmode.state.DEBUG)
    #execmode.state.set_state(execmode.state.RELEASE)
    execmode.logging.set_color_diagnostics(True)

    # parse args
    _print_header()
    run_state = _do_args()

    # parse config
    try: 
        cfg = parse_yaml_cfg(open(run_state.config, "r"))
    except FileNotFoundError:
        fatal_error("could not read %s" % run_state.config)
    except yaml.parser.ParserError as ex:
        print("error parsing config:", file=sys.stderr)
        fatal_error(str(ex))
        sys.exit(1)
        

    # load generator module
    try: 
        run_state.module = init_module(cfg['generator']['type'])
    except ImportError:
        fatal_error("invalid project type %s.  use %s --list-types\n" % \
                    (cfg['generator']['type'], sys.argv[0]))
        

    # debug dump config
    if execmode.state.get_state() == execmode.state.DEBUG:
        import pprint
        _pp = pprint.PrettyPrinter(indent=2)
        _pp.pprint(cfg)

    # begin project generation/refresh
    try:
        refresh_project(cfg, run_state.module, run_state.out_path,
                        run_state.config)
    except RefreshError as re:
        fatal_error(re)
        
    
