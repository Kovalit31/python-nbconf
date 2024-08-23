'''
A new simple scripting library/console with extending on Python.

For moddding tutorial, refer to /docs/api/index.md
For usage, refer to /docs/usage.md
'''

from .__main__ import main
from . import core
from . import lib
import os


reg = {
    "struct.Result": lib.structs.Result,
    "struct.Result.Ok": lib.structs.Ok,
    "struct.Result.Err": lib.structs.Err,
    "lib.io.print": lib.io.printf,
    "lib.fs.object.File": lib.fs.File,
    "lib.fs.object.Dir": lib.fs.Dir,
    "lib.api.function.can_disable": lib.api.can_disable,
    "core.config.get": lib.conf.get_conf,
    "core.runtime.RuntimeData": core.runtime.RuntimeData,
    "core.runtime.SetupRuntime": core.runtime.SetupRuntime,
    "lib.functions.get_relroot": lib.utils.get_relroot,
    "lib.functions.module.import_mod": lib.imp.import_module,
    "lib.functions.module.unimport_mod": lib.imp.unimport_module,
    "var.const.default_mods": os.path.join(os.path.dirname(__file__), "mods"),
}

def setup_runtime() -> None:
    core.runtime.SetupRuntime(reg)
