'''
Utilities for nbconf
'''
import random
import string
import os

from . import structs

def clean_empty(data: list) -> list:
    _p = []
    for pos, x in enumerate(data):
        if len(x.strip() if isinstance(x, str) else x) == 0:
            _p.append(pos-len(_p))
    for y in _p:
        data.pop(y)
    return data


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

def remove_same(s1, s2):
    first = None
    for x in range(max(len(s1), len(s2))):
        if x >= len(s1):
            first = True
            break
        elif x >= len(s2):
            first = False
            break
        elif s1[x] != s2[x]:
            break
    return s1[x:] if not first else "", s2[x:] if first or first is None else ""

def get_relroot(root: str, path: str) -> str:
    root = os.path.abspath(os.path.expanduser(root))
    path = os.path.abspath(os.path.expanduser(path))
    if root in path:
        rel_root = path[len(root):].replace("\\","/").lstrip("/")
    else:
        s1, s2 = remove_same(root, path)
        rel_root = "/"*(("/"+s1.lstrip("/")).count("/"))+s2 if len(s1) > 0 else s2
    rel_root = "nbconf_root" if len(rel_root) == 0 else "nbconf_root/"+rel_root
    return rel_root