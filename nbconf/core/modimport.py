from typing import Callable
from nbconf.lib.structs import Err, Ok

def resolve_symbol(self, symbol, mod, helpers):
    if helpers is None:
        return Err("Helpers is None!")
    for x in helpers:
        if x(self, symbol, mod).is_ok():
            return Ok()
    return Ok() # Probably we haven't got associations

## CORE FUNCTIONS

def _set_exportable(self, symbol, mod):
    return Err()

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