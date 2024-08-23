import subprocess
import nbconf_root as _root # type: ignore
import sys
import os

_Ok = _root.struct.Result.Ok

def _jmp_mutate(self, runtime, additional):
    cur = runtime.next - 1
    variables = self._mutate_vars
    result = additional
    if result is None:
        return _root.struct.Result.Err("jmp_mutate can't be used without Result data")
    if result.is_ok():
        pass
    else:
        pass
    return _Ok()

def export(self, args):
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

@_root.lib.api.function.can_disable("enable_exec")
def system_exec(_, args):
    print(args)
    a = subprocess.run(args, capture_output=True)
    print(a.stdout.decode())
    if a.stderr:
        print("While running command expected next errors")
        print(a.stderr.decode())
    return _Ok(a.stdout)

@_root.lib.api.function.can_disable("enable_exec", "enable_shell")
def shell(_, args):
    while True:
        a = input()
        if a == "exit":
            return _Ok()
        elif a == "":
            continue
        else:
            print(subprocess.run([a], shell=True, text=True).stdout)

def source(runtime, args):
    return insmod(runtime, args)

@_root.lib.api.function.can_disable("enable_ext_insmod")
def insmod(runtime, args):
    for x in args:
        if os.path.exists(x):
            runtime._import_mod(_root.lib.functions.get_relroot(_root.var.const.default_mods, os.path.dirname(x)), x)
    return _Ok()

@_root.lib.api.function.can_disable("enable_ext_rdmod", "enable_ext_insmod", "enable_ext_rmmod")
def rdmod(runtime, args):
    for x in args:
        if not x in runtime._mod_path:
            continue
        path = runtime._mod_path[x]
        rmmod(runtime, [x])
        insmod(runtime, [path])
    return _Ok()

def lsmod(runtime, args):
    if len(args) == 0:
        print(f"Imported modules: {(a:=' '.join([x for x in runtime._mod_assoc]))}")
    else:
        a = []
        for x in args:
            if x in runtime._mod_assoc:
                print(x)
                a.append(x)
            else:
                print(x+": No such module") # Error
    return _Ok(a)

@_root.lib.api.function.can_disable("enable_ext_rmmod")
def rmmod(runtime, args):
    a = lsmod(runtime, []).unwrap()
    for x in args:
        if x in a:
            mod = sys.modules[x]
            for y in runtime._mod_assoc[x]:
                b = runtime._cmd_reg.pop(y, None)
                del(b)
            runtime._mod_assoc.pop(x, None)
            _root.lib.functions.module.unimport_mod(mod, x)
    return _Ok()

__MUTATE = {
    "vars": {},
    # funtions: [PRESTART, POSTSTART]
    "functions": [[], [_jmp_mutate]]
}

#__EXPORTABLE = {
#   "functions": {"cmd_name": function} or [function],
#   "other": {"author": author, "version": version}
#}