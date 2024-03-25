'''
Runtime initialization and lifetime
'''

import sys
import os
import re
from typing import Callable

from ..utils import printf
from ..utils.structs import Result
from ..utils.imp_hook import import_module, unimport_module

SETUP_NAME = "nbconf_root"

class SetupRuntime:
    '''
    Setups globally accessed data
    '''
    def __init__(self, setup_defs: dict) -> None:
        for x, y in setup_defs.items():
            setattr(self, x, y) 
        sys.modules[SETUP_NAME] = self

class RuntimeData:
    '''
    Runtime data storage worker
    '''
    _cmd_reg = {}
    _variables = {"SHELL": SETUP_NAME, "PWD": os.getcwd()}

    def __init__(self) -> None:
        pass

    def _import_mods(self, module_path) -> None:
        '''
        Imports modules
        @param module_path Is a path to modules
        '''
        if module_path is None:
            return
        for root, dirs, files in os.walk(module_path):
            py_files = [x for x in files if not x.startswith("_") and x.endswith(".py")]
            if len(py_files) == 0:
                continue
            rel_root = root.removeprefix(os.path.abspath(os.path.expanduser(module_path))).lstrip("/")
            rel_root = "nbconf_root" if len(rel_root) == 0 else rel_root
            for x in py_files:
                modname = rel_root.replace("/", ".")+"."+x
                path = os.path.join(root, x)

                _result = import_module(modname, path)
                _mod = _result._data if _result.is_ok() else None
                if _mod == None:
                    continue
                for y in dir(_mod):
                    if y.startswith("_"):
                        continue
                    _f = getattr(_mod, y)
                    if not isinstance(_f, Callable):
                        continue
                    self._cmd_reg[y] = _f

def run(runtime: RuntimeData, data: str) -> object:
    '''
    Runs commands in @param data with @param runtime runtime
    '''
    from .language import lex, generate, pregenerate
    _commands = pregenerate(lex(data))
    _pos = 0
    result = None
    while _pos < len(_commands):
        _command = generate(runtime, _commands[_pos])
        if len(_command[0]) == 0:
            printf(f"There is no command at {_pos}", level='e')
        elif len(_command[0]) == 1 and _command[0][0].startswith("-"):
            result = _command[0][0][1:]
        elif not _command[0][0] in runtime._cmd_reg:
            printf(f"No such command: '{_command[0][0]}'!", level='e')
        else:
            result = runtime._cmd_reg[_command[0][0]](runtime, _command[0][1:]).unwrap()
            #if result.is_err():
            #    printf(f"Run error! Exception: {str(result._err)}", level='f')
        _pos += 1
    return result if result is not None else "undef"
