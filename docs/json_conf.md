# JSON configuration

Supported sections:

- "modules" -- Path to modules. 
- "flags" -- Enabled flags

## Section "modules"

Contains: path to root directory (string) of modules.
Default: None => Not loading custom modules.

All \*.py in this path recursively will be imported into runtime and functions
will be linked as command-line function.

## Section "flags"

Contains: list of enabled flags, that used to protect/grant access to specific function(s)/feature(s)
Default: list of False => Default behavior of commands

For example, flag "enable_hello_world" of core module enables hello_world function, but flag "disable_exec" disables any execution of custom commands through system shell.