'''
I/O library
'''
from .structs import Result

import platform
import sys

if platform.system().lower().startswith('linux'):
    import readline

class Print:
    _stdout = print

    def __init__(self, runtime) -> None:
        self._fatal = True
        self.runtime = runtime

    def print(self, *message, level="i", ehandler=Exception):
        '''
        Formats message with level.
        Exit, when fatal. Like in customcmd.
        @param string (str): Output string
        @param level (str): Info level ([d]ebug|[v]erbose|[i]nfo|[e]rror|[w]arning|[f]atal) (Default: i)
        '''
        string = " ".join([str(x) for x in message])
        _level = level[0].lower().strip()
        _levels = {
            "f": "&",
            "e": "@",
            "w": "!",
            "d": '~',
            'i': "*",
            "v": ".",
            "c": "`",
        }
        if _level == 'd' and not self.runtime.exported_var["DEBUG"]:
            return
        if _level == 'v' and not self.runtime.exported_var["VERBOSE"]:
            return
        msg = f"[{_levels[_level] if _level in _levels else '?'}] {string}".replace("\n", "\n[`] ")
        self._stdout(msg)
        #global_log.write_log(msg) # TODO Logger (may be via script command)
        if _level == 'f' and self._fatal:
            if not self.runtime._variables["VERBOSE"]:
                exit(2)
            raise ehandler(msg)
    
    def error(self, *message):
        _message = message
        if len(message) == 1 and isinstance(message[0], Result):
            _message = [str(message[0]._err)]
        self.print(*_message, level="e")
    
    def info(self, *message):
        self.print(*message, level="i")

    def debug(self, *message):
        self.print(*message, level='d')
    
    def fatal(self, *message, handler=Exception):
        _message = message
        if len(message) == 1 and isinstance(message[0], Result):
            if message[0].is_err():
                _message = [str(message[0]._err)]
                handler = message[0]._err.__class__
            else:
                _message = [str(message[0]._data)]
        self.print(*_message, level="f", ehandler=handler)