'''
Import hooks for importing non-module python code
'''

from .structs import Result, Ok, Err

import importlib.util
import sys
import types

def import_module(name: str, path: str) -> Result:
    if name in sys.modules:
        return Ok(sys.modules[name])
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        return Err(Exception(f"Invalid module {name} spec"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if spec.loader is None:
        return Err(Exception("spec loader is None"))
    spec.loader.exec_module(module)
    return Ok(module)

def unimport_module(module: types.ModuleType, name: str) -> Result:
    try:
        sys.modules.pop(name)
        del(module)
        return Ok()
    except:
        return Err(Exception("?"))

