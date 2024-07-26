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
- RuntimeData._mod_aliases: dict[str, str] - Aliases for modded command execution
- RuntimeData._mod_pattern: dict[str, Any] - Pattetns of data, which are used internally, processing command mods
- RuntimeData._mod_assoc - Undocumented yet
- RuntimeData._mod_path - Undocumented yet
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
________<br>
CAUTION!<br>
————————<br>
1. You mustn't print (leak) variables (also in debug!)
2. You mustn't use variables like PWD or smth like, use internal functions! These variables only for scripting!
3. You have to not use non-predefined variables without checking


### RuntimeData._import_mods

Function that tries to load all (!) py files from module_path. Can fail) <br>
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
