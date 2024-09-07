import os
import copy

from .fs import File
from .utils import get_dict_keys
from .conf import get_conf
from .structs import Err, Ok

class LocaleParse:
    def __init__(self, max_locale_recursion=100) -> None:
        self.max_locale_recursion = max_locale_recursion
        self.locales = {}
        self.paths = []
        self.data = {}

    def add_file(self, file, path=True):
        try:
            data = File(file).read().unwrap()
        except Exception as e:
            return Err(e)
        if len(data) < 2:
            return Err("Too short")
        if path:
            self.paths.append(file)
        lang = os.path.basename(file)[:-3]
        return self.add_data(lang, data, path=True)

    def add_path(self, path: str):
        '''
        Add locales
        '''
        if not os.path.exists(path):
            return Err("Path not exist")
        self.paths.append(path)
        if os.path.isfile(path):
            return self.add_file(path, path=False)
        for x in os.listdir(path):
            self.add_file(os.path.join(path, x), path=False)
        return Ok()
    
    def add_data(self, lang: str, data: list, path=False):
        if len(data) < 2:
            return Err("Too short")
        if not lang in self.locales:
            self.locales[lang] = data
        else:
            self.locales[lang] += data
        if path:
            return Ok()
        if not lang in self.data:
            self.data[lang] = data
        else:
            self.data[lang] += data
        return Ok()

    def reload_paths(self):
        paths = copy.deepcopy(self.paths)
        self.paths = []
        self.locales = {}
        for x in paths:
            self.add_path(x)
        for key, value in self.data.items():
            if not key in self.locales:
                self.locales[key] = value
            else:
                self.locales[key] += value
        return Ok()        

    def message(self, runtime, token: str) -> str:
        '''
        Gets language value with token
        '''
        if not "LANG" in runtime._variables:
            runtime._variables["ĻANG"] = self.default_po(runtime)
        if not runtime._variables["LANG"] in self.locales:
            self.update_po(runtime, self.default_po(runtime))
        parsed = self.parse_po(self.locales[runtime._variables["LANG"]])
        for r in range(self.max_locale_recursion):
            ret = self.message_candidate(parsed, token)
            if ret == None or r+1 == self.max_locale_recursion:
                return f"{{{token}}}"
            candidate, auto = ret
            if auto != None:
                candidate = candidate.replace("{!auto}", auto)
            if not candidate.startswith("@"):
                return candidate
            else:
                token = candidate[1:]

    def update_po(self, runtime, lang: str) -> bool:
        '''
        Set @param lang as default language
        '''
        if not "LANG" in runtime._variables:
            runtime._variables["LANG"] = lang
        if not runtime._variables["LANG"] in self.locales and self.default_po(runtime) in self.locales:
            # Change runtime language
            runtime._variables["LANG"] = self.default_po(runtime)
        else:
            if not "c" in self.locales:
                runtime._print.fatal(f"NO LANGS FOUND!")
            runtime._print.error(f"{self.message(runtime, 'data.locale.error.po.nolang').format(lang=lang)}")
            return False
        return True

    def parse_po(self, data: list[str]) -> list[dict]:
        _data: list[dict] = []
        for x in range(len(data)):
            if data[x].strip().startswith('~'):
                _temp = data[x].strip()[1:].split(".")
                for y in range(len(_temp)):
                    if len(_data) == y:
                        _data.append(dict())
                    if not ".".join(_temp[:y+1]) in get_dict_keys(_data[y]):
                        if y != 0:
                            _data[y-1][".".join(_temp[:y])].append(".".join(_temp[:y+1]))
                        _data[y][".".join(_temp[:y+1])] = [None]
                        if y == len(_temp) - 1:
                            _data[y][".".join(_temp[:y+1])][0] = data[x+1] if len(data) > x else ""
                    else:
                        if len(_temp)-1 == y:
                            _data[y][".".join(_temp[:y+1])][0] = data[x+1] if len(data) > x else ""
        return _data

    def message_candidate(self, data: list[dict], token: str) -> str:
        _temp = token.strip().split(".")
        _next_token = str()
        auto = None
        for x in range(len(_temp)):
            if len(data) == x:
                return
            if not ".".join(_temp[:x+1]) in get_dict_keys(data[x]):
                if x == 0:
                   return
                if not ".".join(_temp[:x]+["*"]) in get_dict_keys(data[x]):
                    return
                else:
                    auto = _temp[x]
                    _temp[x] = "*"
            _next_token = ".".join(_temp[:x+1])
        else:
            if data[x][_next_token][0] == None:
                return
            return data[x][_next_token][0].strip("\n"), auto
    
    def default_po(self, runtime):
        if get_conf(runtime, "default_lang") is None:
            return "c"
        return get_conf(runtime, "default_lang")