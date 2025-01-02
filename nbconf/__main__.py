'''
Main runner
'''

from .core import runtime
from .lib import conf
from .lib import fs
from .core import language

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

def _cmd_apply_mutate(_, runtime, __):
    runtime._critical = False

def _cmd_revert_mutate(_, runtime, __):
    runtime._critical = True

def _main(args: argparse.Namespace) -> None:
    from . import reg
    runtime.LegacyRuntime.exported_var.update({"DEBUG": args.debug, "VERBOSE": args.verbose})
    _runtime = runtime.RuntimeData(language.gen, language.jit)
    _runtime.setup_runtime(reg)
    _runtime.exported_var["CONF"] = _runtime.exported_var["PWD"] if args.config is None else args.config
    _runtime.exported_var.update({"DEBUG": args.debug, "VERBOSE": args.verbose})
    _runtime.importer.default_path = os.path.join(os.path.dirname(__file__), "mods")
    _runtime.importer._import_module_path(_runtime, os.path.join(os.path.dirname(__file__), "mods"))
    _runtime.importer._import_module_path(_runtime, conf.get_conf(_runtime,"modules"))
    _runtime._locale.add_path(os.path.join(os.path.dirname(__file__), "locale"))
    if args.config is None and args.FILE is None:
        _runtime.mutator.register_apply_mutate(1, _cmd_apply_mutate)
        _runtime.mutator.register_clear_mutate(1, _cmd_revert_mutate)
        _cmds = ""
        while True:
            try:
                _cmds = input(_runtime.exported_var["PS1"])
                runtime.run(_runtime, _cmds)
            except (SystemExit, EOFError):
                print()
                sys.exit()
            except:
                continue
    if args.FILE is not None:
        script = "".join(fs.File(args.FILE, touch=False).read().unwrap()) # type: ignore
        runtime.run(_runtime, script)
        sys.exit()
    runtime.run(_runtime, "hello_world -- no_err no_msg")

if __name__ == "__main__":
    main()
