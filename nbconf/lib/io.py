'''
I/O library
'''

import platform
import sys

if platform.system().lower().startswith('linux'):
    import readline

def printf(*message, runtime, level="i", ehandler=Exception):
    '''
    Formats message with level.
    Exit, when fatal. Like in customcmd.
    @param string (str): Output string
    @param level (str): Info level ([d]ebug|[v]erbose|[i]nfo|[e]rror|[w]arning|[f]atal) (Default: i)
    '''
    string = " ".join(message)
    _level = level[0].lower().strip()
    if _level == 'd' and not runtime._variables["DEBUG"]:
       return
    if _level == 'v' and not runtime._variables["VERBOSE"]:
       return
    msg = f"[{'*' if _level == 'i' else '!' if _level == 'w' else '@' if _level == 'e' else '~' if _level == 'd' else '.' if _level == 'v' else '&' if _level == 'f' else '?'}] {string}".replace("\n", "\n[`] ")
    print(msg)
    #global_log.write_log(msg) # TODO Logger (may be via script command)
    if _level == 'f':
        if not runtime._variables["VERBOSE"]:
            exit(2)
        raise ehandler(msg)