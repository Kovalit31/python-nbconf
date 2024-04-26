'''
Utilities for nbconf (like printf, io utc.)
'''
import platform
from . import structs, imp_hook

def printf(*message, level="i"):
    '''
    Formats message with level.
    Exit, when fatal. Like in customcmd.
    @param string (str): Output string
    @param level (str): Info level ([d]ebug|[v]erbose|[i]nfo|[e]rror|[w]arning|[f]atal) (Default: i)
    '''
    string = " ".join(message)
    _level = level[0].lower().strip()
    #if _level == 'd' and not definitions["debug"]:
    #    return
    #if _level == 'v' and not definitions["verbose"]:
    #    return
    msg = f"[{'*' if _level == 'i' else '!' if _level == 'w' else '@' if _level == 'e' else '~' if _level == 'd' else '.' if _level == 'v' else '&' if _level == 'f' else '?'}] {string}".replace("\n", "\n[`] ")
    print(msg)
    #global_log.write_log(msg)
    if _level == 'f':
        if True: # TODO Use of global conf
            exit(2)
        raise Exception(msg)

def clean_empty(data: list) -> list:
    _p = []
    for pos, x in enumerate(data):
        if len(x.strip() if isinstance(x, str) else x) == 0:
            _p.append(pos-len(_p))
    for y in _p:
        data.pop(y)
    return data

def system_is_linux() -> bool:
    return platform.system().lower().startswith('linux')

