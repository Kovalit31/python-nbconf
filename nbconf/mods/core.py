import nbconf_root as _root # type: ignore
import sys
import os

_Ok = _root.struct.Result.Ok

def export(self, args):
    return self._cmd_reg["declare"](self, ["-x"] + args)

def set(self, args):
    return _Ok()

def declare(self, args):
    print(args)
    return _Ok()

def exit(self, args):
    sys.exit()

def hello_world(_, __):
    print("Hello world!")
    return _Ok()

@_root.lib.api.function.can_disable("enable_exec")
def system_exec(_, __):
    return _Ok()

@_root.lib.api.function.can_disable("enable_source")
def source(runtime, args):
    for x in args:
        if os.path.exists(x):
            runtime._import_mod()
    return _Ok()