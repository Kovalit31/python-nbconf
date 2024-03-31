'''
Main runner
'''

from .core import runtime
from .core import language
from .core import conf

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

def _main(args: argparse.Namespace) -> None:
    from . import setup_runtime
    setup_runtime()
    _runtime = runtime.RuntimeData()
    _runtime._variables["CONF"] = _runtime._variables["PWD"] if args.config is None else args.config
    _runtime._import_mods(os.path.join(os.path.dirname(__file__), "mods"))
    _runtime._import_mods(conf.get_conf(_runtime,"modules"))
    _runtime._variables["DEBUG"] = args.debug
    if args.config is None and args.FILE is None:
        while True:
            try:
                _cmds = input() # TODO PS1
            except:
                print()
                continue
            runtime.run(_runtime, _cmds)
    if args.FILE is not None:
        script = "".join(fs.File(args.FILE, touch=False).read().unwrap())
        runtime.run(_runtime, script)
        sys.exit()
    runtime.run(_runtime, "hello_world -- no_err no_msg")
#     print((a :=language.lex("hello \"?world?\" (?cat?) ?(cat)? # jmp_rel 2; hello -- jmp_rel 2")), (b:=language.pregenerate(a)), language.generate(runtime.RuntimeData(), b[1]))


if __name__ == "__main__":
    main()
