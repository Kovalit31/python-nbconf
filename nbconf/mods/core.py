import subprocess
import nbconf_root as _root # type: ignore
import sys
import os
import re

_Ok = _root.lib.struct.Result.Ok

# ---------- Mutate ----------- #

def _jmp_mutate(self, runtime, additional):
    cur = runtime.instructions[1] - 1
    result = additional
    if result is None:
        return _root.lib.struct.Result.Err("jmp_mutate can't be used without Result data")
    _i = cur + 1
    suf = "pos" if result.is_ok() else "neg"
    # suf jump, then relative suf jump, then normal jump, then normal relative jump
    if f"jmp_{suf}" in self._mutate_vars:
        _i = self._mutate_vars[f"jmp_{suf}"]
    elif f"jmp_r{suf}" in self._mutate_vars:
        _i += self._mutate_vars[f"jmp_r{suf}"]
    elif "jmp_n" in self._mutate_vars:
        _i = self._mutate_vars["jmp_n"]
    elif "jmp_rn" in self._mutate_vars:
        _i += self._mutate_vars["jmp_rn"]
    if _i >= len(runtime.instructions[0]) and runtime.instructions[1] < len(runtime.instructions[0]):
        return _Ok()
    runtime.instructions[1] = _i
    return _Ok()

# ----------    Casting    ----------- #

def str_to_int(string: str):
    if not re.match("^[+-]?\d+$", string.strip()):
        return _root.lib.struct.Result.Err("Input data not correct")
    return int(string)

# ---------- Base commands ----------- #
def export(self, args):
    '''
    Exports variable
    @return variable - Variable
    @return value - Value of
    Works as bash's export
    '''
    _parsed = "".join(args)
    if len(_parsed.strip()) == 0:
        return _root.lib.struct.Result.Err("No args")
    __parsed = _parsed
    start, end = _root.lib.functions.utils.char_indexes(__parsed, "=")
    while end - start > 0:
        if len(__parsed) > end and __parsed[end-1] == "\\":
            __parsed = __parsed[:end-1] + (__parsed[end+1:] if len(__parsed) > end+1 else "")
            start, end = _root.lib.functions.utils.char_indexes(__parsed, "=")
            continue
        return _root.lib.struct.Result.Err("More than one setting")
    if start-1 >= 0 and _parsed[start-1] == "\\":
        _parsed = _parsed[:start-1] + _parsed[start:]
    smth = _parsed.split("=", maxsplit=1)
    if len(smth) < 2:
        return _root.lib.struct.Result.Err("No setting") 
    # TODO Serializators?
    if smth[1].isdigit():
        smth[1] = int(smth[1])
    self._variables[smth[0]] = smth[1]
    return _Ok()

def help(runtime, _):
    runtime.print.info(f"Available commands: {' '.join(sorted([x for x in runtime._cmd_reg.keys()]))}")
    return _Ok()

def exit(self, args):
    sys.exit()

# ------------ Hello world -------------- #
@_root.lib.functions.api.can_enable("enable_hello_world")
def hello_world(runtime, __):
    runtime.print.debug("Hello world!")
    return _Ok()

@_root.lib.functions.api.can_enable("enable_hello_world")
def hello(runtime, args):
    runtime.print.debug(runtime._locale.message(runtime, 'io.github.kovalit31.nbconf.mod.core.hello'))
    return _Ok()

# ------------ Sys exec ------------- #

@_root.lib.functions.api.can_disable("disable_exec")
def system_exec(runtime, args):
    runtime.print.debug(args)
    a = subprocess.run(args, capture_output=True)
    runtime.print.info(a.stdout.decode())
    if a.stderr:
        runtime.print.error("While running command expected next errors")
        runtime.print.print(a.stderr.decode(), level="c")
    return _Ok(a.stdout)

@_root.lib.functions.api.can_disable("disable_exec", "disable_shell")
def shell(runtime, args):
    while True:
        a = input()
        if a == "exit":
            return _Ok()
        elif a == "":
            continue
        else:
            runtime.print.info(subprocess.run([a], shell=True, text=True).stdout)

# ------------- Modules -------------- #

def source(runtime, args):
    return insmod(runtime, args)

@_root.lib.functions.api.can_disable("disable_ext_insmod")
def insmod(runtime, args):
    for x in args:
        if os.path.exists(x):
            runtime.importer._import_module(runtime, _root.lib.functions.runtime.get_relroot(_root.var.const.core.mod_import.default_mods, os.path.dirname(x)), x)
    return _Ok()


@_root.lib.functions.api.can_disable("disable_ext_rdmod", "disable_ext_insmod", "disable_ext_rmmod")
def rdmod(runtime, args):
    for x in args:
        if not x in runtime.module["assoc"]:
            continue
        path = runtime.module["path"][runtime.module["assoc"][x]]
        rmmod(runtime, [x])
        insmod(runtime, [path])
    return _Ok()

def lsmod(runtime, args):
    if len(args) == 0:
        a = ' '.join([x for x in runtime.module["assoc"].keys()])
    else:
        a = []
        for x in args:
            if x in runtime.module["assoc"]:
                a.append(x)
            else:
                runtime.print.error(runtime._locale.message(runtime, "io.github.kovalit31.nbconf.mod.core.lsmod.mod_not_found").format(module=x)) # Error
    runtime.print.info(f"Imported modules: {a}")
    return _Ok(a)

@_root.lib.functions.api.can_disable("disable_ext_rmmod")
def rmmod(runtime, args):
    for x in args:
        if x in runtime.module["assoc"]:
            mod = runtime.module["assoc"][x]
            for y in runtime.module["func"][runtime.module["assoc"][x]]:
                b = runtime.command_registry.pop(y, None)
                del(b)
            runtime.module["assoc"].pop(x, None)
            _root.lib.functions.module.unimport_mod_file(mod, x)
    return _Ok()

# -------------- Locale ----------------- #

# TODO May be disabled?
def locale_reload(runtime, args):
    return runtime._locale.reload_paths()

# --------------- Signatures ----------------- #

__MUTATE = {
    "vars": {
        "jmp_n": int,
        "jmp_rn": int,
        "jmp_pos": int,
        "jmp_rpos": int,
        "jmp_neg": int,
        "jmp_rneg": int
    },
    # apply/clear: [PRESTART, POSTSTART]
    "apply": [[], [_jmp_mutate]],
    "casting": [[str, int, str_to_int]]
}

__EXPORTABLE = {
    "other": {
        "author": "Kovalit31",
        "version": "0.0.2-b"
    },
    "locale": [
        "lang/c.po"
    ]
}