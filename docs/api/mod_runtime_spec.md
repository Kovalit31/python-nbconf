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
# nbconf -> $ my_runtime
# Hello world!
```

## Symbols
For full symbol reference, read nbconf/__init__.py <br>

## Internal hacks

For creating functions, you can simply... Create Python function!</br>
But, if you don't want to export all functions...</br>
Probably, we have only 2 ways:</br>
1. Add '\_' before function name (like '\_my_secret_function')
2. Write \_\_EXPORTABLE variable (see [EXPORTABLE] section)
 
Also you can create custom mutators (but you need to refer [Main runtime specification](./main_runtime_spec.md)) (see [MUTATE] section)</br>

### EXPORTABLE

\_\_EXPOTABLE structure is used for defining information, that is being exported.</br>
Structure definitions is:</br>
```python
__EXPORTABLE = {
    "functions": ["my_func"], # Or {"my_func_command_name": my_func}
    "other": {
        "author": "AUTHOR",
        "version": "0.0.0"
    }
}
```
</br>

### MUTATE
\_\_MUTATE structure is used for defining mutate functions and variables.
Structure definition is:<br>
```python
__MUTATE = {
    "vars": {"my_variable": bool},  # Or other type; this is pattern
    "functions": [[prestart_func], [poststart_func]] # For each stage it's own array
}
```