'''
Main header
'''

from .__main__ import main
from . import utils
from . import core
from . import lib
import os


reg = {
    "struct.Result": utils.structs.Result,
    "struct.Result.Ok": utils.structs.Ok,
    "struct.Result.Err": utils.structs.Err,
    "lib.io.print": utils.printf,
    "lib.fs.object.File": lib.fs.File,
    "lib.fs.object.Dir": lib.fs.Dir,
    "lib.api.function.can_disable": lib.api.can_disable,
    "core.config.get": lib.conf.get_conf,
    "lib.functions.get_relroot": utils.get_relroot,
    "lib.functions.module.import_mod": utils.imp_hook.import_module,
    "lib.functions.module.unimport_mod": utils.imp_hook.unimport_module,
    "var.const.default_mods": os.path.join(os.path.dirname(__file__), "mods"),
}

def setup_runtime() -> None:
    core.runtime.SetupRuntime(reg)
