'''
Language model code for nbconf
'''

from .runtime import RuntimeData
from ..utils import printf

import string

letters = {x: "LETTER" for x in string.ascii_letters}
punctuation = {x: "PUNCTUATION" for x in string.punctuation}
digits = {x: "DIGIT" for x in string.digits}

special = {
    "\\": "BACKSLASH",
    "#": "COMMENT",
    "\'": "QUOTE",
    "\"": "DOUBLE_QUOTE",
    "?": "VARIABLE",
    "(": "PARENTHESS_LEFT",
    ")": "PARENTHESS_RIGHT",
    "-": "DASH",
    " ": "WHITESPACE",
    "\n": "NLINE",
    ";": "NLINE",
}

def lex(data: str) -> list[list[str]]:
    '''
    Parses @param data to lexical tokens
    '''
    lex_dict = {}
    for x in [letters, digits, punctuation, special]:
        lex_dict.update(x)
    tokens = [] # list[list[str]] or [[token, value]]
    for pos, y in enumerate(data):
        try:
            tokens.append([lex_dict[y], y])
        except KeyError:
            printf(f"Unknown symbol while parsing: '{y}' at {pos}", level='e')
    return tokens

def pregenerate(tokens: list[list[str]]) -> list[list[list[list[list[str]]]]]:
    '''
    Actually is ast analyzer, but very simplified
    @param tokens is output of lex
    '''
    generated = [[[[]], [[]]]] # [command: [cmd: [string_tokens: []], [<same situation>]]
    dash = False
    comment = False
    ignore_special = False
    cpart = 0
    varname = []
    varswitch = False
    quote = False
    double = False
    parenthess_stack = []
    wr = True
    a = False
    lq = 0

    write_token = lambda token: generated[-1][cpart][-1].append(token) if not varswitch else varname.append(token)

    def break_variable(*_) -> None:
        for x in [["IGNORED_VARIABLE", "?"]] + varname[1:]:
            write_token(x)
        varname = []
        varswitch = False

    for pos, token in enumerate(tokens):
        parenthess = len(parenthess_stack) > 0
        tname, _ = token
        if tname == "DASH":
            if not comment and not quote:
                wr = False
                if ignore_special:
                    ignore_special = False
                    wr = True
                elif dash:
                    if varswitch and not parenthess:
                        break_variable()
                    dash = False
                    cpart = (cpart + 1) % 2
                else:
                    if varswitch:
                        break_variable()
                    dash = True
                    a = True
        elif tname == "WHITESPACE":
            if not comment and not quote:
                if not ignore_special:
                    if varswitch and not parenthess:
                        break_variable()
                    wr = False
                    if len(generated[-1][cpart]) > 0:
                        generated[-1][cpart].append([])
                else:
                    ignore_special = False
        elif tname == "NLINE":
            if comment:
                comment = False
            if not ignore_special:
                if varswitch and not parenthess:
                    break_variable()
                if quote:
                    printf(f"Oops! Unterminated quotes at {pos}! NOTE: {lq} is latest open quote", level='f')
                wr = False
                generated.append([[[]], [[]]])
                cpart = 0
            else:
                ignore_special = False
        elif tname == "BACKSLASH":
            if not comment:
                if not ignore_special:
                    ignore_special = True
                else:
                    wr = False
                    ignore_special = False
        elif tname == "VARIABLE":
            if not comment and (quote and double):
                if not ignore_special:
                    if varswitch and not parenthess:
                        varswitch = False
                        for y in varname:
                            write_token(y)
                    elif not parenthess:
                        varswitch = True
                else:
                    token = ["IGNORED_VARIABLE", "?"]
                    ignore_special = False
        elif tname == "COMMENT":
            if not comment and not quote:
                if not ignore_special:
                    if varswitch and not parenthess:
                        break_variable()
                    comment = True
                else:
                    ignore_special = False
        elif tname == "QUOTE":
            if not comment:
                if not ignore_special:
                    if varswitch and not parenthess:
                        break_variable()
                    if quote and not double:
                        quote = False
                    elif not quote:
                        quote = True
                        lq = pos
                else:
                    ignore_special = False
        elif tname == "DOUBLE_QUOTE":
            if not comment:
                if not ignore_special:
                    if varswitch and not parenthess:
                        break_variable()
                    if quote and double:
                        quote = False
                        double = False
                    elif not quote:
                        quote = True
                        double = True
                        lq = pos
                else:
                    ignore_special = False
        elif tname == "PARENTHESS_RIGHT":
            if parenthess and parenthess_stack[-1] == "(":
                parenthess_stack.pop()
            else:
                printf(f"Oops! Unterminated parenthess at {pos}!", level='f')
        elif tname == "PARENTHESS_LEFT":
            parenthess_stack.append("(")
        if not comment:
            if (tname == "DASH" and dash) and not a:
                write_token(["PUNCTUATION", "-"])
                dash = False
            else:
                a = False
        if not wr:
            wr = True
            continue
        if comment:
            continue
        write_token(token)
    return generated

def generate(runtime: RuntimeData, cmd: list[list[list[list[str]]]]) -> list[list[str]]:
    '''
    JIT. Processes variables, may work with RuntimeData
    @param runtime Current process runtime
    @param cmd Current command to exec (generate(lex("smth"))[x])
    '''
    from .runtime import run
    generated = [[""], [""]]
    for ppos, cpart in enumerate(cmd):
        for _, s in enumerate(cpart):
            if len(generated[ppos][-1]) != 0:
                generated[ppos].append("")
            var = False
            vardata = ""
            for _, t in enumerate(s):
                if t[0] == "VARIABLE":
                    if var:
                        if vardata.startswith("(") and vardata.endswith(")"):
                            vardata = vardata.strip("()") 
                            data = run(runtime, vardata)
                            generated[ppos][-1] += str(data)
                        else:
                            try:
                                generated[ppos][-1] += runtime._variables[vardata]
                            except KeyError:
                                printf(f"Unknown variable '{vardata}'", level='e')
                        var, vardata = False, ""
                        continue
                    var = True
                    continue
                if var:
                    vardata += t[1]
                    continue
                generated[ppos][-1] += t[1]
    return generated

