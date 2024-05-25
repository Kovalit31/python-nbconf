import nbconf_root as _root
import sys

_Ok = _root.struct.Result.Ok

def export(self, args): # Copy-paste bash :)
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
