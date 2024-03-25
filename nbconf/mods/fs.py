import sys
try:
    _nbconf = sys.modules["nbconf_root"]
except KeyError:
    raise ImportError("Not running in nbconf runtime, exit!")

_Ok = getattr(_nbconf, "struct.Result.Ok")
_Err = getattr(_nbconf, "struct.Result.Err")

def mkdir(self, args):
    return _Ok()

def rmdir(self, args):
    return _Ok()

def touch(self, args):
    return _Ok()

def rm(self, args):
    return _Ok()

def mv(self, args):
    return _Ok()

def cp(self, args):
    return _Ok()

def ls(self, args):
    return _Ok()

def ln(self, args):
    return _Ok()

