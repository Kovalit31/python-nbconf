# JSON configuration

Supported sections:

- "modules" -- Path to modules.

## Section "modules"

Contains: path to root directory (string) of modules.
Default: None => Not loading custom modules.

All \*.py in this path recursively will be imported into runtime and functions
will be linked as command-line function.
