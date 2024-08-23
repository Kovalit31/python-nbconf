from nbconf.lib.structs import Ok, Err
# Stages

MUTATE_STAGE_PRESTART = 0
MUTATE_STAGE_POSTSTART = 1

class MutateData:
    _private_data = {}
    _stages = []
    _mutate_pattern = {}
    _mutate_vars = {}

    def register_mutate_pattern(self, mutate_pattern: dict):
        self._mutate_pattern.update(mutate_pattern)
        return Ok()

    def register_mutate_var(self, mutate_var, data=None):
        if not mutate_var in self._mutate_pattern:
            return Err("Register pattern for {} first".format(mutate_var))
        if self._mutate_pattern[mutate_var] != bool and data is None:
            return Err("Register data for non-boolean type {} cannot be None".format(mutate_var))
        if self._mutate_pattern[mutate_var] == bool:
            self._mutate_vars[mutate_var] = True
            return Ok()
        if not isinstance(data, self._mutate_pattern[mutate_var]):
            return Err(NotImplementedError("Type casting not implemented yet"))
        self._mutate_vars[mutate_var] = data
        return Ok()

    def register_mutate(self, stage, func, after=None, before=None):
        if len(self._stages) <= stage:
            self._stages = self._stages + [[]] * (stage - len(self._stages) + 1)
        if after is None and before is None:
            self._stages[stage].append(func)
            return Ok()
        return Err(NotImplementedError("Before and after currently unimplemented"))
        
    def apply_mutate(self, stage, runtime, additional=None):
        if len(self._stages) <= stage:
            # Probably we doesn't registered mutate functions, so abort exec
            return Err("Stage not initializated")
        errored = []
        for x in self._stages[stage]:
            try:
                x(self, runtime, additional)
            except:
                errored.append(x)
        return Ok(errored)
    
    def needs_value_var(self, mutate_var):
        if not mutate_var in self._mutate_pattern:
            return Err("Register pattern for {} firstly".format(mutate_var))
        if self._mutate_pattern[mutate_var] == bool:
            return Ok(False)
        return Ok(True)