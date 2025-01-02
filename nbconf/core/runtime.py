'''
Runtime initialization and lifetime
'''

import sys
import os

from nbconf.core.modimport import ModImporter, DEFAULT_HELPERS
from nbconf.core.mutate import MutateData

from nbconf.lib.utils import set_rattr
from nbconf.lib.io import Print
from nbconf.lib.structs import Err
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
        LegacyRuntime.print.debug(" ".join([x for x in dir(self) if not x.startswith("__")]))
        # TODO Legacy
        sys.modules[SETUP_NAME] = self # type: ignore

class RuntimeData:
    '''
    Runtime data storage worker
    '''

    def __init__(self, gen, jit) -> None:
        self.command_registry = {}
        self.exported_var = {"SHELL": SETUP_NAME, "PWD": os.getcwd(), "PS1": "nbconf -> $ ", "<<": None, "LANG": "c"}
        self.module = {
            "assoc": {},
            "func": {},
            "path": {},
            "reg_data": {}
        }
        self.mutator = MutateData()
        self._locale = LocaleParse()
        self.print = Print(self)
        self.importer = ModImporter(os.path.join(os.path.dirname(__file__), "mods"), DEFAULT_HELPERS)
        self.instructions = [[], 1] # [ instructions, next_instruction ]
        self.private_var = {}
        self._critical = True
        self._critical_message = True
        self.language = {"generator": gen, "compiler": jit}
        self.setup = None
    
    def setup_runtime(self, registry: dict) -> None:
        self.setup = SetupRuntime(registry)

    def set_default_module_path(self, def_mod_path: str) -> None:
        self.importer.default_path = def_mod_path

LegacyRuntime = RuntimeData(None, None)

def clean_runtime(runtime: RuntimeData):
    runtime.mutator._mutate_vars = {}
    runtime.mutator._private_data = {}
    runtime.private_var = {}

def run(runtime: RuntimeData, data: str):
    '''
    Runs commands in date with runtime
    @param data Raw commands 
    @param runtime runtime
    '''
    runtime.instructions[0] = runtime.language["generator"](data)
    runtime.instructions[1] = 0
    runtime.print.debug(runtime.instructions)
    result = None
    while runtime.instructions[1] < len(runtime.instructions[0]):
        cur_command = runtime.language["compiler"](runtime, runtime.instructions[0][runtime.instructions[1]])
        runtime.instructions[1] += 1
        
        if len(cur_command[0]) == 0:
            runtime.print.debug(f"There is no command at {runtime.instructions[1]}")
            continue
        
        wait_next = False
        for m_pos, mutate in enumerate(cur_command[1]):
            if wait_next:
                b = runtime.mutator.register_mutate_var(cur_command[1][m_pos-1], mutate)
                if b.is_err():
                    runtime.print.debug(f"Error processing mutate var '{mutate}' because of {b._err}")
            if (a:=runtime.mutator.needs_value_var(mutate)).is_ok() and a.unwrap():
                wait_next = True
                continue
        
        runtime.mutator.apply_mutate(0, runtime)
        try:
            result = runtime.command_registry[cur_command[0][0]](runtime, cur_command[0][1:])
        except SystemExit as e:
            raise e
        except Exception as e:
            result = Err(f"Can't run command {cur_command[0][0]}: {str(e)}")
            runtime.print.error(result)
        runtime.mutator.apply_mutate(1, runtime, result)
        
        if runtime._critical and result.is_err():
            if runtime._critical_message:
                runtime.print.fatal(result._err)
            sys.exit()
        
        runtime.mutator.clear_mutate(1, runtime, result)
        clean_runtime(runtime)