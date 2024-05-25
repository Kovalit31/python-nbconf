'''
Utilities for nbconf (like printf, io utc.)
'''
import platform
import random
import string
from . import structs, imp_hook

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

def resolve_jump(cur: int, jmp_data: dict[str, int], is_pos: bool) -> int:
    _i = cur + 1
    suf = "pos" if is_pos else "neg"
    if jmp_data[f"jmp_{suf}"]:
        _i = jmp_data[f"jmp_{suf}"]
    elif jmp_data[f"jmp_n"]:
        _i = jmp_data[f"jmp"]
    elif jmp_data[f"jmp_r{suf}"]:
        _i += jmp_data[f"jmp_r{suf}"]
    elif jmp_data[f"jmp_rn"]:
        _i += jmp_data[f"jmp_rn"]
    return _i

def random_uuid(length=20) -> str:
    """
    Generates uuid from digits and lowercase ascii letters
    """
    return "".join(
        random.choices([*(string.ascii_lowercase + string.digits)], k=length)
    )

def get_rattr(cl: object, rpath: list) -> object:
    _temp = cl
    for x in rpath:
        x = x.strip()
        if x in dir(_temp):
            _temp = getattr(_temp, x)
        else:
            return None
    return _temp

def set_rattr(cl: object, rpath: list, value: object):
    path = [cl]
    if rpath[-1].strip() == "_self":
        return
    for x in rpath[:-1]:
        x = x.strip()
        if x == "_self":
            return
        if x in dir(path[-1]):
            if not isinstance(getattr(path[-1], x), structs.Empty):
                z = structs.Empty()
                setattr(z, "_self", getattr(path[-1], x))
                path.append(z)
                continue
            path.append(getattr(path[-1], x))
        else:
            path.append(structs.Empty())
    path.append(value)
    path = path[::-1]
    rpath = rpath[::-1]
    if rpath[-1] in dir(path[-2]):
        return
    for xpos, x in enumerate(rpath):
        setattr(path[xpos+1], x, path[xpos])

