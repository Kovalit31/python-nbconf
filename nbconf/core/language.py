'''
Language model code for nbconf
'''

from dataclasses import dataclass
from nbconf.core.runtime import LegacyRuntime
from nbconf.lib.io import printf

import string
import re

@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int

def tokenize(data):
    '''
    Tokenizer
    '''
    spec = [
        ("COMMENT", r'([#].*$|[/][*].*[*][/])'),
        ("VARIABLE", r'[?](\w+|[\(].*[\)]|[{].*[}])[?]'),
        ("QUOTE", r'(?<!\\)[\']'),
        ("DOUBLE", r'(?<!\\)["]'),
        ("SWITCH", r'[-][-]'),
        ("IGN_END", r'\\(;|\n)'),
        ("END", r'(;|\n)'),
        ("SKIP", r'[ \t\n]+'),
        ("NUMBER", r'(\+|\-)?\d+(\.\d*)?'),
        ("MISMATCH", r'[^\u0020-\u007F]+'.format(
            re.escape(
                string.printable.split(" ")[0]
                ).replace("\\", "\\\\")
            )),
        ("SYM", r'.')
    ]
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in spec)
    line = 1
    start = 0
    quote = False
    double = False
    for tok in re.finditer(tok_regex, data):
        _type = tok.lastgroup
        value = tok.group()
        _column = tok.start() - start
        if _type == "END" and value == "\n":
            start = tok.end()
            line += 1
        elif _type == "QUOTE":
            if not double:
                quote ^= True
                continue
            else:
                _type = "SYM"
        elif _type == "DOUBLE":
            if not quote:
                double ^= True
                continue
            else:
                _type = "SYM"
        elif _type == "SKIP" or _type == "IGN_END":
            if not (quote or double):
                continue
            _type = "SYM"
        elif _type != "SYM" and _type != "MISMATCH" and quote:
            __column = _column
            for x in value:
                yield Token("SYM", x, line, __column)
                __column += 1
            continue
        elif _type == "MISMATCH":
            printf(f"Mismatch at line {line}:{_column}!", runtime=LegacyRuntime, level='d')
            continue
        elif _type == "COMMENT":
            continue
        yield Token(_type if _type is not None else "UNKNOWN", value, line, _column)

def gen(data):
    '''
    Generator of command data. Uses tokenizer
    data: str - Script
    return: list[list[list[structs.Token]]]
    '''
    cmds = [[[],[]]] # cmds: [ cmd: [ self: [], mod: []]]
    part = 0
    for x in tokenize(data):
        if x.type == "END":
            part = 0
            cmds.append([[],[]])
            continue
        elif x.type == "SWITCH":
            part = (part+1)%2
            continue
        else:
            cmds[-1][part].append(x)
    return cmds

def jit(runtime, cmd):
    '''
    JIT. Processes all tokens into end command
    runtime: RuntimeData - Current runtime
    cmd: list[list[structs.Token]] - Command (gen(sth)[x])
    '''
    from .runtime import run
    ret = []
    for ppos, part in enumerate(cmd):
        ret.append([""])
        for tpos, tok in enumerate(part):
            join = False
            if tpos > 0:
                prev = part[tpos-1]
                join = prev.column+len(prev.value) == tok.column
            _ret = tok.value
            if tok.type == "VARIABLE":
                _data = tok.value[1:-1]
                _ret = None
                if len(_data) > 4 and _data[::len(_data)-1] == "()":
                    printf(f"Inline command detected at {tok.column}", runtime=runtime, level='d')
                    run(runtime, _data[1:-1])
                    _ret = runtime._variables["<<"]
                    printf(str(_ret), runtime=runtime, level='d')
                else:
                    if len(_data) > 4 and _data[::len(_data)-1] == "{}":
                        _data = _data[1:-1]
                    try:
                        _ret = runtime._variables[_data]
                    except KeyError:
                        printf(f"May be incorrect: {_data} variable returned None", runtime=runtime, level='d')
                        pass
            if not join:
                if len(ret[ppos][-1].strip()) > 0:
                    ret[ppos].append("")
            if _ret is not None:
                ret[ppos][-1] += _ret
        if len(ret[-1]) == 1 and len(ret[-1][-1]) == 0:
            ret[-1] = []
    return ret
