'''
Runtime initialization and lifetime
'''

import copy
import sys
import os
from typing import Callable

from ..utils import printf, resolve_jump, set_rattr, get_relroot
from ..utils.structs import Err, Ok
from ..utils.imp_hook import import_module

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
    _mod_aliases = {
        "%": "err_msg",
    }
    _mod_pattern = {
        "jmp_neg": 0,
        "jmp_rneg": 0,
        "jmp_rpos": 0,
        "jmp_pos": 0,
        "jmp_rn": 0,
        "jmp_n": 0,
        "err_msg": "",
        "no_exit": False,
        "no_msg": False,
    }
    _mod_assoc = {}
    _mod_path = {}

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
        self._mod_path[modname] = file
        for y in dir(_mod):
            if y.startswith("_"):
                continue
            if y in self._cmd_reg:
                continue
            _f = getattr(_mod, y)
            if not isinstance(_f, Callable):
                continue
            self._cmd_reg[y] = _f
            if not modname in self._mod_assoc:
                self._mod_assoc[modname] = [y]
            else:
                self._mod_assoc[modname].append(y)

LegacyRuntime = RuntimeData()

def run(runtime: RuntimeData, data: str):
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
        mod_data = copy.deepcopy(runtime._mod_pattern)
        if runtime._variables["DEBUG"]:
            print(cur_command)
        if len(cur_command[0]) == 0:
            printf(f"There is no command at {_pos}", runtime=runtime, level='d')
            _pos += 1
            continue
        else:
            result = Err(f"Command '{cur_command[0][0]}' not found!")
            runtime._variables["<<"] = None
            runtime._variables["<?"] = 255
            if cur_command[0][0] in runtime._cmd_reg:
                try:
                    result = runtime._cmd_reg[cur_command[0][0]](runtime, cur_command[0][1:])
                except Exception as e:
                    printf(f"Can't run command {cur_command[0][0]}: {e}", runtime=runtime, level='e')
                    break
                runtime._variables["<?"] = 0
            else:
                printf(f"Command '{cur_command[0][0]}' not found!", runtime=runtime, level='e')
            wait_next = False
            for m_pos, mod in enumerate(cur_command[1]):
                if mod in runtime._mod_aliases and not wait_next:
                    mod = runtime._mod_aliases[mod]
                    cur_command[1][m_pos] = mod
                if wait_next:
                    try:
                        mod_data[cur_command[1][m_pos-1]] = type(mod_data[cur_command[1][m_pos-1]])(mod)
                        wait_next = False
                    except:
                        printf(f"Can't set {mod} as type {type(mod_data[cur_command[1][m_pos-1]])}", runtime=runtime, level='d')
                    continue
                if not mod in mod_data:
                    printf(f"Mod not found {mod}!", runtime=runtime, level='e')
                    continue
                if not isinstance(mod_data[mod], bool):
                    wait_next = True
                    continue
                mod_data[mod] = not mod_data[mod]
            jump_data = {x: y for x,y in mod_data.items() if x.startswith("jmp_")}
            __pos = resolve_jump(_pos, jump_data, result.is_ok())
            if __pos >= len(command_list) and _pos + 1 < len(command_list):
                printf("Can't calculate good jump! Can't continue execution: no instruction", runtime=runtime, level='f')
            _pos = __pos
            if result.is_ok():
                runtime._variables["<<"] = result.unwrap()
            else:
                error = str(result._err)
                if len(mod_data["err_msg"]) > 0:
                    error = mod_data["err_msg"]
                if mod_data["no_msg"]:
                    error = None
                if mod_data["no_exit"]:
                    runtime._variables["<?"] = 2 # TODO Fix this
                    continue
                if error is not None:
                    printf(error, runtime=runtime, level='f')
                else:
                    sys.exit(2) # TODO Fix this
    # return result
