from typing import Callable
from nbconf.lib.io import printf
from nbconf.lib.structs import Err, Ok

def _set_exportable(self, symbol, mod):
    if "EXPORTABLE" in self._private_data:
        data = self._private_data["EXPORTABLE"]
        if data["functions"] and isinstance(getattr(mod, symbol), Callable):
            return Ok()
    else:
        self._private_data["EXPORTABLE"] = {"functions": False}
    if symbol != "__EXPORTABLE":
        return Err()
    exportable = getattr(mod, symbol)
    if "functions" in exportable:
        self._private_data["EXPORTABLE"]["functions"] = True
        functions = exportable["functions"]
        if isinstance(functions, dict):
            for x, y in functions.items():
                if x in self._cmd_reg:
                    from nbconf.core.runtime import LegacyRuntime
                    printf("Can't register, already registered: {}".format(x), LegacyRuntime, level='d')
                    continue
                if mod in self._mod_func:
                    self._mod_func[mod].append(x)
                else:
                    self._mod_func[mod] = [x]
                self._cmd_reg[x] = y
        if isinstance(functions, list):
            for x in functions:
                if x in mod:
                    f = getattr(mod, x)
                    if mod in self._mod_func:
                        self._mod_func[mod].append(x)
                    else:
                        self._mod_func[mod] = [x]
                    self._cmd_reg[x] = f
    if "other" in exportable:
        self._mod_reg_data[mod] = exportable["other"]
    return Ok()

def _set_mutate(self, symbol, mod):
    return Err()

def _set_function(self, symbol, mod):
    if symbol.startswith("_"):
        return Err()
    if symbol in self._cmd_reg:
        return Err()
    _f = getattr(mod, symbol)
    if not isinstance(_f, Callable):
        return Err()
    self._cmd_reg[symbol] = _f
    if not mod in self._mod_func:
        self._mod_func[mod] = [symbol]
    else:
        self._mod_func[mod].append(symbol)
    return Ok()

DEFAULT_HELPERS = [_set_exportable, _set_mutate, _set_function]

def resolve_symbol(self, symbol, mod, helpers):
    if helpers is None:
        return Err("Helpers is None!")
    for x in helpers:
        if x(self, symbol, mod).is_ok():
            return Ok()
    return Ok() # Probably we haven't got associations

def default_resolve_symbol(self, symbol, mod):
    return resolve_symbol(self, symbol, mod, DEFAULT_HELPERS)