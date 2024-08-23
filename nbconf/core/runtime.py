'''
Runtime initialization and lifetime
'''

import copy
import sys
import os
from typing import Callable

from nbconf.core.modimport import _set_function, resolve_symbol
from nbconf.core.mutate import MutateData

from nbconf.lib.utils import resolve_jump, set_rattr, get_relroot
from nbconf.lib.io import printf
from nbconf.lib.structs import Err, Ok
from nbconf.lib.imp import import_module

SETUP_NAME = "nbconf_root"

class SetupRuntime:
    '''
    Setups globally accessed data
    '''
    def __init__(self, setup_defs: dict) -> None:
        for x, y in setup_defs.items():
            a = x.split(".")
            set_rattr(self, a, y)
        printf(" ".join([x for x in dir(self) if not x.startswith("__")]), runtime=LegacyRuntime, level='d')
        sys.modules[SETUP_NAME] = self # type: ignore

class RuntimeData:
    '''
    Runtime data storage worker
    '''
    _cmd_reg = {}
    _variables = {"SHELL": SETUP_NAME, "PWD": os.getcwd(), "PS1": "nbconf -> $ ", "<<": None}
    _mod_func = {}
    _mod_assoc = {}
    _mod_path = {}
    _mod_reg_data = {}
    _mutate = MutateData()
    _instructions = []
    _next = 1
    _private_data = {}

    def _import_mods(self, def_mod_path, module_path) -> None:
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
            rel_root = get_relroot(def_mod_path, root)
            for x in py_files:
                self._import_mod(rel_root, os.path.join(root, x))

    def _import_mod(self, rel_root: str, file: str) -> None:
        modname = rel_root.replace("/", ".")+"."+".".join(os.path.basename(file).split(".")[:-1])
        _result = import_module(modname, file)
        _mod = _result._data if _result.is_ok() else None
        if _mod == None:
            return
        if _mod in self._mod_path:
            return
        self._mod_path[_mod] = file
        self._mod_assoc[modname] = _mod
        for y in dir(_mod):
            resolve_symbol(self, y, _mod, [_set_function])

LegacyRuntime = RuntimeData()

def run(runtime: RuntimeData, data: str):
    '''
    Runs commands in date with runtime
    @param data Raw commands 
    @param runtime runtime
    '''
    from .language import gen, jit
    runtime._instructions = gen(data)
    runtime._next = 0
    if runtime._variables["DEBUG"]:
        print(runtime._instructions)
    result = None
    while runtime._next < len(runtime._instructions):
        cur_command = jit(runtime, runtime._instructions[runtime._next])
        runtime._next += 1
        if runtime._variables["DEBUG"]:
            print(cur_command)
        if len(cur_command[0]) == 0:
            printf(f"There is no command at {runtime._next - 1}", runtime=runtime, level='d')
            continue
        elif not cur_command[0][0] in runtime._cmd_reg:
            result = Err(f"Command '{cur_command[0][0]}' not found!")    
            printf(f"Command '{cur_command[0][0]}' not found!", runtime=runtime, level='e')
        else:
            wait_next = False
            for m_pos, mutate in enumerate(cur_command[1]):
                if wait_next:
                    runtime._mutate.register_mutate_var(cur_command[1][m_pos-1], mutate)
                if (a:=runtime._mutate.needs_value_var(mutate)).is_ok() and a.unwrap():
                    wait_next = True
                    continue
            runtime._mutate.apply_mutate(0, runtime)
            #runtime._variables["<<"] = None
            #runtime._variables["<?"] = 255 TODO: Think about serialization/deserialization
            try:
                result = runtime._cmd_reg[cur_command[0][0]](runtime, cur_command[0][1:])
            except Exception as e:
                result = Err(f"Can't run command {cur_command[0][0]}: {e}")
            #runtime._variables["<?"] = 0 TODO: That is good idea, but need to refactor
            runtime._mutate.apply_mutate(1, runtime, result)
    #         jump_data = {x: y for x,y in mod_data.items() if x.startswith("jmp_")}
    #         __pos = resolve_jump(runtime._next, jump_data, result.is_ok())
    #         if __pos >= len(runtime._instructions) and runtime._next + 1 < len(runtime._instructions):
    #             printf("Can't calculate good jump! Can't continue execution: no instruction", runtime=runtime, level='f')
    #         runtime._next = __pos
    #         if result.is_ok():
    #             runtime._variables["<<"] = result.unwrap()
    #         else:
    #             error = str(result._err)
    #             if len(mod_data["err_msg"]) > 0:
    #                 error = mod_data["err_msg"]
    #             if mod_data["no_msg"]:
    #                 error = None
    #             if mod_data["no_exit"]:
    #                 runtime._variables["<?"] = 2 # TODO Fix this
    #                 continue
    #             if error is not None:
    #                 printf(error, runtime=runtime, level='f')
    #             else:
    #                 sys.exit(2) # TODO Fix this
    # # return result
