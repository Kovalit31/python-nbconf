# Main runtime specification

Runtime is provided by RuntimeData object. <br>
Basically, you don't need to use it, even you won't create command-line in your program. <br>

## Setup

If you reached that it may need for you, then create instance by acquiring this: <br>

```python
# You need to import nbconf_root!
runtime = nbconf_root.core.runtime.RuntimeData()
runtime._import_mods(nbconf_root.var.const.default_mods)
# OR register functions by example
runtime._cmd_reg["my_func"] = my_func # CAUTION: Do not place parenteses after function! It will not work!
```

## Defined objects/function/variables

- RuntimeData._cmd_reg: dict[str, function] - Map between command-line commands and they handler functions
- RuntimeData._variables: dict[str, Any] - Map between command-line variables and some data
- RuntimeData._mod["func"]: dict[Module, list[str]] - Map between modules and their functions names
- RuntimeData._mod["assoc"]: dict[str, Module] - Map between module names and theirs modules
- RuntimeData._mod["path"]: dict[Module, str] - Map between module and his location path
- RuntimeData._mutate: MutateData - Mutator, defined for this runtime
- RuntimeData._next: int - Next command index (Must be processed by runner and/or by MutateData)
- RuntimeData._instructions - Current instructions (Must be defined by runner)
- RuntimeData._import_mods(def_mod_path: str, module_path: str) - Check below
- RuntimeData._import_mod(rel_root: str, file: str) - Check below

## Examples of usage

### RuntimeData._cmd_reg

```python
def myfunc():
    print("Hello world!")

runtime = nbconf_root.runtime.RuntimeData()
# Setting function
runtime._cmd_reg["myfunc"] = myfunc
# Getting function
myfunc = runtime._cmd_reg["myfunc"]
myfunc()
# Output: Hello world!
```

### RuntimeData._variables

```python
runtime = nbconf_root.runtime.RuntimeData()
# Setting variable
runtime._variables["VAR"] = "somerandomtext"
# Getting variable
print(runtime._variables["VAR"])
```

CAUTION!<br>
1. You mustn't print (leak) variables (also in debug!)
2. You mustn't use variables like PWD or smth like, use internal functions! These variables only for scripting!
3. You have to not use non-predefined variables without checking


### RuntimeData._import_mods

Function that tries to load all (!) py files from module_path. May fail <br>
Example: <br>
```python
runtime = nbconf_root.runtime.RuntimeData()
runtime._import_mods(nbconf_root.var.const.default_mods, "/path/to/your/modules")
```

### RuntimeData._import_mod

Function that tries to load mod file. May fail.<br>
Example:<br>
```python
runtime = nbconf_root.runtime.RuntimeData()
runtime._import_mod(nbconf_root.lib.functions.get_relroot(nbconf_root.var.const.default_mods, "/path/to/file.py"), "/path/to/same/file")
```
