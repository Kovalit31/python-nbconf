# Mod runtime specification

By default, almost after start, system loading nbconf.core.runtime.SetupRuntime 
object, that loads all components, defined in nbconf.reg, and then loads itself 
in sys.modules as nbconf_root. <br>
It works because: <br>
1. You write import statement
2. Python lookups sys.modules for module; if Python find out it there, it going to import
3. If Python can't find out module, it goes to load py file.
4. If file can't be found, it fails. <br>
So, we are hooking second step. Believe, that Python 4 won't brick this! <br>

## Setup your own runtime
CAUTION: DO NOT OVERRIDE nbconf_root!!!<br>
```python
# Your main mod
import nbconf_root

def _symbol():
    print("Hello world")

_reg = {
   "path.to.symbol": symbol,
}
def my_runtime(self, args):
    nbconf_root.core.runtime.SetupRuntime("my_runtime", reg)
    # Then create RuntimeData, import mod and run command
    return nbconf_root.struct.Result.Ok()

## mod.py
import my_runtime

def my_cmd():
    my_runtime.path.to.symbol()

## Nbconf console
nbconf -> $ my_runtime
Hello world!
```

## Symbols
For full reference, read nbconf/__init__.py <br>

