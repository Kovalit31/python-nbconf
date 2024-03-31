import sys
import argparse
try:
    _nbconf = sys.modules["nbconf_root"]
except KeyError:
    raise ImportError("Not running in nbconf runtime, exit!")

_Ok = getattr(_nbconf, "struct.Result.Ok")
_Err = getattr(_nbconf, "struct.Result.Err")

def _donothing(*_, **__):
    return None

def echo(self, args):
    _exit = sys.exit
    sys.exit = _donothing
    try:
        parser = argparse.ArgumentParser("echo", exit_on_error=False)
        parser.add_argument("TEXT", nargs="*")
        _args = parser.parse_args(args)
        print(" ".join(_args.TEXT))
    except ValueError:
        sys.exit = _exit
        return _Err("Nothing good!")
    sys.exit = _exit
    return _Ok()

def read(self, args):
    return _Ok()
