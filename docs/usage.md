# Usage

## Initializating project

### 1. Creating scripts
  
Create build/scripts or some else directory in your build directory and  
create scripts that you wish to use.  
  
To be continued. (To do)  
  
### 2. Write custom commands

Create directory in your build directory.  
Add "modules" section in 'nbconf.json' (for more details, refer to  
[JSON configuration](json_conf.md)) with directory path as a string.  
In this directory create python file with some name (To do), and write following:

    import sys as \_sys
    \_root = \_sys.modules["nbconf\_root"]
    \_Ok = getattr(\_root, "struct.Result.Ok")
    def hello\_world(\_, \_):
        print("Hello world!")
        return \_Ok()


