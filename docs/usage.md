# Usage

## Initializating project

### 1. Creating scripts
To do
### 2. Write custom commands

1. Create directory in your work directory.
2. Add "modules" section in 'nbconf.json' (for more details, refer to
[JSON configuration](json_conf.md)) with directory path as a string.<br>
Example:<br>

```json
{
    "modules": "." // This directory
}

```
3. In this directory create python file with some name (To do), and write following:

```
import nbconf_root

def hello_world(_, _):
    print("Hello world!")
    return nbconf_root.struct.Result.Ok()
```
More tutor on this you can get [here](api/index.md).

### 3. Debugging / Testing commands

Nbconf can be runned. For this, simply call 'nbconf' (if you installed with pip)</br>
or use 'python3 -m nbconf --help' for help information.