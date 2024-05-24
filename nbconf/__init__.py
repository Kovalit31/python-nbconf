'''
Main header
'''

from .__main__ import main
from . import utils
from . import core
from . import lib


reg = {
    "struct.Result": utils.structs.Result,
    "struct.Result.Ok": utils.structs.Ok,
    "struct.Result.Err": utils.structs.Err,
    "lib.io.print": utils.printf,
    "lib.fs.object.File": lib.fs.File,
    "lib.fs.object.Dir": lib.fs.Dir,
    "core.config.get": core.conf.get_conf,
}

def setup_runtime() -> None:
    core.runtime.SetupRuntime(reg)
