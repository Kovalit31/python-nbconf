import sys
try:
    _nbconf = sys.modules["nbconf_root"]
except KeyError:
    raise ImportError("Not running in nbconf runtime, exit!")

_Ok = getattr(_nbconf, "struct.Result.Ok")

def export(self, args): # Copy-paste bash :)
    return self._cmd_reg["declare"](self, ["-x"] + args)

def set(self, args):
    return _Ok()

def declare(self, args):
    print(args)
    return _Ok()

def exit(self, args):
    sys.exit()
    return _Ok() # Never go here

