try:
    import nbconf_root # type: ignore
    module = True
except:
    module = False

__version__ = "0.0.2"
__autor__ = "Kovalit31"

'''
Debugtools for nbconf
This module CAN'T USE ANY of dependencies from root. All this dependencies need to be written here
Purpose of this module is debugging some API methods.
'''

def __debugshell():
    while True:
        cmd = input("!debugshell (from debugtools) >>> ")
        cmd = cmd.strip()
        if cmd == "exit":
            break
        elif cmd == "version":
            print(f"debugshell {__version__} for nbconf by {__autor__}")
            continue
        elif cmd == "":
            continue
        yield cmd

def __debugprint(msg: str):
    print("[DEBUG] "+msg)

def __seeker(what: object):
    _temp = [what]
    for x in __debugshell():
        if x.startswith("./"):
            z = x[2:].rstrip()
            if z in dir(_temp[-1]):
                _temp.append(getattr(_temp[-1], z))
            else:
                __debugprint("no attribute associated")
            continue
        elif x.startswith("../"):
            if len(_temp) > 1:
                _temp.pop()
            continue
        elif x.startswith(".?"):
            __debugprint(" ".join(dir(_temp[-1])))
        elif x.startswith("//"):
            __debugprint(str(_temp))
        elif x.startswith("_"):
            a = x[1:].split(" ")
            try:
                b = getattr(_temp[-1], a[0])
                print(str(b(*a[1:])))
            except Exception as e:
                __debugprint(f"not supported: {str(e)}")
        else:
            if x.startswith("\\"):
                a = x.lstrip("\\")
            else:
                a = x
            if not a in dir(_temp[-1]):
                __debugprint("no attribute associated")
                continue
            __debugprint(str(getattr(_temp[-1], a)))

class _Ok():
    _data = None
    def is_ok(self):
        return True
    def is_err(self):
        return False
    def unwrap(self):
        return None

if module:
    def module_seek(_, __):
        __seeker(nbconf_root)
        return _Ok()

def runtime_seek(runtime, __):
    __seeker(runtime)
    return _Ok()

__EXPORTABLE = {
    "other": {
        "author": __autor__,
        "version": __version__
    }
}