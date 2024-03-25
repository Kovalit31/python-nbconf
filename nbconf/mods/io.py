import sys
try:
    _nbconf = sys.modules["nbconf_root"]
except KeyError:
    raise ImportError("Not running in nbconf runtime, exit!")

_Ok = getattr(_nbconf, "struct.Result.Ok")

def echo(self, args):
    return _Ok()

def read(self, args):
    return _Ok()
