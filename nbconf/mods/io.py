import sys
import argparse
import nbconf_root as _root # type: ignore

_Ok = _root.struct.Result.Ok
_Err = _root.struct.Result.Err

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
    return _Ok(" ".join(_args.TEXT))

def read(self, args):
    return _Ok()
