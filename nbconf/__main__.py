'''
Main runner
'''

from .core import runtime
from .lib import conf
from .lib import fs

import os
import sys
import argparse

def _parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NBCONF runner")
    parser.add_argument("--debug", required=False, action="store_true", help="Debug mode")
    parser.add_argument("--verbose", required=False, action="store_true", help="Verbose mode")
    parser.add_argument("FILE", nargs="?", default=None, metavar="SCRIPT", help="Interpreter script (useful for #! on linux)")
    parser.add_argument("--config", "-c", default=None, type=str, required=False, help="Configuration file")
    return parser.parse_args()

def main() -> None:
    _main(_parse())

def _cmd_apply_mutate(mutator, runtime, additional):
    runtime._critical = False

def _cmd_revert_mutate(mutator, runtime, additional):
    runtime._critical = True

def _main(args: argparse.Namespace) -> None:
    from . import setup_runtime
    runtime.LegacyRuntime._variables.update({"DEBUG": args.debug, "VERBOSE": args.verbose})
    setup_runtime()
    _runtime = runtime.RuntimeData()
    _runtime._variables["CONF"] = _runtime._variables["PWD"] if args.config is None else args.config
    _runtime._import_mods(os.path.join(os.path.dirname(__file__), "mods"), os.path.join(os.path.dirname(__file__), "mods"))
    _runtime._import_mods(os.path.join(os.path.dirname(__file__), "mods"), conf.get_conf(_runtime,"modules"))
    _runtime._variables.update({"DEBUG": args.debug, "VERBOSE": args.verbose})
    _runtime._locale.add_path(os.path.join(os.path.dirname(__file__), "locale"))
    if args.config is None and args.FILE is None:
        _runtime._mutate.register_apply_mutate(1, _cmd_apply_mutate)
        _runtime._mutate.register_clear_mutate(1, _cmd_revert_mutate)
        _cmds = ""
        while True:
            try:
                _cmds = input(_runtime._variables["PS1"])
            except:
                print()
                continue
            runtime.run(_runtime, _cmds)
    if args.FILE is not None:
        script = "".join(fs.File(args.FILE, touch=False).read().unwrap()) # type: ignore
        runtime.run(_runtime, script)
        sys.exit()
    runtime.run(_runtime, "hello_world -- no_err no_msg")

if __name__ == "__main__":
    main()
