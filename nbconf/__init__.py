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
    "lib.struct.Result": lib.structs.Result,
    "lib.struct.Result.Ok": lib.structs.Ok,
    "lib.struct.Result.Err": lib.structs.Err,
    "lib.fs.object.File": lib.fs.File,
    "lib.fs.object.Dir": lib.fs.Dir,
    "lib.functions.api.can_disable": lib.api.can_disable,
    "lib.functions.api.can_enable": lib.api.can_enable,
    "lib.core.config.get_section": lib.conf.get_conf,
    "lib.core.config.get_flag": lib.conf.get_flag,
    "lib.core.runtime.RuntimeData": core.runtime.RuntimeData,
    "lib.core.runtime.SetupRuntime": core.runtime.SetupRuntime,
    "lib.functions.runtime.get_relroot": lib.utils.get_relroot,
    "lib.functions.utils.char_indexes": lib.utils.char_indexes,
    "lib.functions.module.import_mod_file": lib.imp.import_module,
    "lib.functions.module.unimport_mod_file": lib.imp.unimport_module,
    "lib.functions.module.ModImporter": core.modimport.ModImporter,
    # TODO Unimporting data
    "var.const.core.mod_import.default_mods": os.path.join(os.path.dirname(__file__), "mods"),
    "var.const.core.mod_import.default_helpers": core.modimport.DEFAULT_HELPERS,
}

def setup_runtime() -> core.runtime.SetupRuntime:
    return core.runtime.SetupRuntime(reg)
