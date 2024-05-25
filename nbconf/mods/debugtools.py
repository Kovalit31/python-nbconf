try:
    import nbconf_root
except:
    raise Exception()

__version__ = "0.0.1"
__autor__ = "Kovalit31"

def __debugshell():
    while True:
        cmd = input("!debugshell (from debugtools) >>> ")
        if cmd == "exit":
            break
        elif cmd == "version":
            print(f"debugshell {__version__} for nbconf by {__autor__}")
            continue
        yield cmd

def __debugprint(msg: str):
    print("[DEBUG] "+msg)

class _Ok():
    data = None
    def is_ok(self):
        return True
    def is_err(self):
        return False
    def unwrap(self):
        return None

def module_seek(_, __):
    _temp = [nbconf_root]
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
        else:
            __debugprint(str(getattr(_temp[-1], x)))
    return _Ok()
