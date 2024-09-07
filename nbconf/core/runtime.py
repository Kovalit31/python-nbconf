'''
Runtime initialization and lifetime
'''

import sys
import os

from nbconf.core.modimport import default_resolve_symbol
from nbconf.core.mutate import MutateData

from nbconf.lib.utils import set_rattr, get_relroot
from nbconf.lib.io import Print
from nbconf.lib.structs import Err
from nbconf.lib.imp import import_module
from nbconf.lib.locale import LocaleParse

SETUP_NAME = "nbconf_root"

class SetupRuntime:
    '''
    Setups globally accessed data
    '''
    def __init__(self, setup_defs: dict) -> None:
        for x, y in setup_defs.items():
            a = x.split(".")
            set_rattr(self, a, y)
        LegacyRuntime._print.debug(" ".join([x for x in dir(self) if not x.startswith("__")]))
        sys.modules[SETUP_NAME] = self # type: ignore

class RuntimeData:
    '''
    Runtime data storage worker
    '''

    def __init__(self) -> None:
        self._cmd_reg = {}
        self._variables = {"SHELL": SETUP_NAME, "PWD": os.getcwd(), "PS1": "nbconf -> $ ", "<<": None, "LANG": "c"}
        self._mod_func = {}
        self._mod_assoc = {}
        self._mod_path = {}
        self._mod_reg_data = {}
        self._mutate = MutateData()
        self._locale = LocaleParse()
        self._print = Print(self)
        self._instructions = []
        self._next = 1
        self._private_data = {}
        self._critical = True
        self._critical_message = True
        self._import_helpers = []
    
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
            default_resolve_symbol(self, y, _mod)

LegacyRuntime = RuntimeData()

def clean_runtime(runtime: RuntimeData):
    runtime._mutate._mutate_vars = {}
    runtime._mutate._private_data = {}
    runtime._private_data = {}

def run(runtime: RuntimeData, data: str):
    '''
    Runs commands in date with runtime
    @param data Raw commands 
    @param runtime runtime
    '''
    from .language import gen, jit
    runtime._instructions = gen(data)
    runtime._next = 0
    runtime._print.debug(runtime._instructions)
    result = None
    while runtime._next < len(runtime._instructions):
        cur_command = jit(runtime, runtime._instructions[runtime._next])
        runtime._next += 1
        runtime._print.debug(cur_command)
        if len(cur_command[0]) == 0:
            runtime._print.debug(f"There is no command at {runtime._next - 1}")
            continue
        else:
            wait_next = False
            for m_pos, mutate in enumerate(cur_command[1]):
                if wait_next:
                    b = runtime._mutate.register_mutate_var(cur_command[1][m_pos-1], mutate)
                    if b.is_err():
                        runtime._print.debug(f"Error processing mutate var '{mutate}' because of {b._err}")
                if (a:=runtime._mutate.needs_value_var(mutate)).is_ok() and a.unwrap():
                    wait_next = True
                    continue
            runtime._mutate.apply_mutate(0, runtime)
            #runtime._variables["<<"] = None
            #runtime._variables["<?"] = 255 TODO: Think about serialization/deserialization
            try:
                result = runtime._cmd_reg[cur_command[0][0]](runtime, cur_command[0][1:])
            except Exception as e:
                result = Err(f"Can't run command {cur_command[0][0]}: {str(e)}")
                runtime._print.error(result)
            #runtime._variables["<?"] = 0 TODO: That is good idea, but need to refactor
            runtime._mutate.apply_mutate(1, runtime, result)
            if runtime._critical and result.is_err():
                if runtime._critical_message:
                    runtime._print.fatal(result._err)
                sys.exit()
            runtime._mutate.clear_mutate(1, runtime, result)
            clean_runtime(runtime)