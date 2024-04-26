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
    _variables = {"SHELL": SETUP_NAME, "PWD": os.getcwd(), "PS1": "nbconf -> $ "} 

    def __init__(self) -> None:
        pass

    def _import_mods(self, module_path) -> None:
        '''
        Imports modules
        @param module_path Is a path to modules
        '''
        if module_path is None:
            return
        for root, _, files in os.walk(module_path):
            py_files = [x for x in files if not x.startswith("_") and x.endswith(".py")]
            if len(py_files) == 0:
                continue
            rel_root = root.removeprefix(os.path.abspath(os.path.expanduser(module_path))).lstrip("/")
            rel_root = "nbconf_root" if len(rel_root) == 0 else rel_root
            for x in py_files:
                modname = rel_root.replace("/", ".")+"."+".".join(x.split(".")[:-1])
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
    from .language import gen, jit
    command_list = gen(data)
    if runtime._variables["DEBUG"]:
        print(command_list)
    _pos = 0
    result = None
    while _pos < len(command_list):
        cur_command = jit(runtime, command_list[_pos])
        if runtime._variables["DEBUG"]:
            print(cur_command)
        if len(cur_command[0]) == 0:
            printf(f"There is no command at {_pos}", level='e')
        elif len(cur_command[0][0]) == 0:
            return None
        elif not cur_command[0][0] in runtime._cmd_reg:
            printf(f"No such command: '{cur_command[0][0]}'!", level='e')
        else:
            result = runtime._cmd_reg[cur_command[0][0]](runtime, cur_command[0][1:]).unwrap()
            #if result.is_err():
            #    printf(f"Run error! Exception: {str(result._err)}", level='f')
        _pos += 1
    return result
