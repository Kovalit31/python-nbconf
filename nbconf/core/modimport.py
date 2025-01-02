import os
from typing import Callable
from nbconf.lib.imp import import_module
from nbconf.lib.structs import Err, Ok
from nbconf.lib.utils import get_relroot

class ModImporter:
    import_helpers = []

    def __init__(self, default_path, helpers=None) -> None:
        self.default_path = default_path
        self.import_helpers += helpers if helpers is not None else []
    
    def resolve_symbol(self, runtime, symbol, mod):
        for x in self.import_helpers:
            if x(runtime, symbol, mod).is_ok():
                return Ok()
        return Ok() # Probably we haven't got associations

    def _import_module_path(self, runtime, module_path) -> None:
        '''
        Imports modules
        @param module_path Is a path to modules
        '''
        if module_path is None:
            return
        for root, _, files in os.walk(module_path):
            modules = [x for x in files if not x.startswith("_") and x.endswith(".py")]
            if len(modules) == 0:
                continue
            rel_root = get_relroot(self.default_path, root)
            for x in modules:
                self._import_module(runtime, rel_root, os.path.join(root, x))

    def _import_module(self, runtime, rel_root: str, file: str) -> None:
        modname = rel_root.replace("/", ".")+"."+".".join(os.path.basename(file).split(".")[:-1])
        result = import_module(modname, file)
        _mod = result.unwrap() if result.is_ok() else None
        if _mod == None:
            runtime.print.error("Module import failed!...")
            return
        if _mod in runtime.module["path"]:
            return
        runtime.module["path"][_mod] = file
        runtime.module["assoc"][modname] = _mod
        for y in dir(_mod):
            self.resolve_symbol(runtime, y, _mod)

def _set_exportable(self, symbol, mod):
    if "EXPORTABLE" in self.private_var:
        data = self.private_var["EXPORTABLE"]
        if data["functions"] and isinstance(getattr(mod, symbol), Callable):
            return Ok()
    else:
        self.private_var["EXPORTABLE"] = {"functions": False}
    if symbol != "__EXPORTABLE":
        return Err()
    exportable = getattr(mod, symbol)
    if "functions" in exportable:
        self.private_var["EXPORTABLE"]["functions"] = True
        functions = exportable["functions"]
        if isinstance(functions, dict):
            for x, y in functions.items():
                if x in self.command_registry:
                    from nbconf.core.runtime import LegacyRuntime
                    LegacyRuntime.print.debug("Can't register, already registered: {}".format(x))
                    continue
                if mod in self.module["func"]:
                    self.module["func"][mod].append(x)
                else:
                    self.module["func"][mod] = [x]
                self.command_registry[x] = y
        if isinstance(functions, list):
            for x in functions:
                if x in mod:
                    f = getattr(mod, x)
                    if mod in self.module["func"]:
                        self.module["func"][mod].append(x)
                    else:
                        self.module["func"][mod] = [x]
                    self.command_registry[x] = f
    if "other" in exportable:
        self.module["reg_data"][mod] = exportable["other"]
    if "locale" in exportable:
        for x in exportable["locale"]:
            res = None
            if os.path.isabs(x):
                res = self._locale.add_path(x)
            else:
                res = self._locale.add_path(os.path.join(os.path.dirname(mod.__file__), x))
            if res.is_err():
                self._print.debug("Locale path doesn't exists: ", x)
    return Ok()

def _set_mutate(self, symbol, mod):
    if symbol != "__MUTATE":
        return Err()
    mutate = getattr(mod, symbol)
    if "vars" in mutate:
        self.mutator.register_mutate_pattern(mutate["vars"])
    if "apply" in mutate:
        for pos, x in enumerate(mutate["apply"]):
            for y in x:
                self.mutator.register_apply_mutate(pos, y)
    if "clear" in mutate:
        for pos, x in enumerate(mutate["clear"]):
            for y in x:
                self.mutator.register_clear_mutate(pos, y)
    if "casting" in mutate:
        for x in mutate["casting"]:
            self.mutator.register_casting(*x)
    return Ok()

def _set_function(self, symbol, mod):
    if symbol.startswith("_"):
        return Err()
    if symbol in self.command_registry:
        return Err()
    _f = getattr(mod, symbol)
    if not isinstance(_f, Callable):
        return Err()
    self.command_registry[symbol] = _f
    if not mod in self.module["func"]:
        self.module["func"][mod] = [symbol]
    else:
        self.module["func"][mod].append(symbol)
    return Ok()

DEFAULT_HELPERS = [_set_exportable, _set_mutate, _set_function]