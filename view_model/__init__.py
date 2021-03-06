from yaml import dump
from functools import wraps
from app_config import config, CONFIG_PATH
from tkinter import Variable, IntVar, BooleanVar, StringVar, DoubleVar

def prefix_function(function, prefunction):
    @wraps(function)
    def run(*args, **kwargs):
        prefunction(*args, **kwargs)
        return function(*args, **kwargs)
    return run

def _hook_init(self, *args, **kwargs):
    self._previous_value = kwargs['value'] if 'value' in kwargs else None

def _hook_set(self, *args, **kwargs):
    try:
        self._previous_value = self.get()
    except:
        self._previous_value = self._default

# this is a terrible idea
Variable.__init__ = prefix_function(Variable.__init__, _hook_init)
Variable.set = prefix_function(Variable.set, _hook_set)

def _create_variable(value):

    assert isinstance(value, (bool, int, float, str)), \
        "Invalid value type: %s" + type(value)

    # bool needs to be first because isinstance(<some_bool>, int) returns true
    if isinstance(value, bool):
        return BooleanVar(
            value=value
            )

    if isinstance(value, int):
        return IntVar(
            value=value
            )

    if isinstance(value, float):
        return DoubleVar(
            value=value
            )

    if isinstance(value, str):
        return StringVar(
            value=value
            )

    raise ValueError(
        "Invalid value type for variable creation: %s" % type(value)
        )

def _dict_to_view_model(src, dst):
    for key, value in src.items():
        dst[key] = _dict_to_view_model(value, {}) \
            if isinstance(value, dict) else _create_variable(value)
    return dst

def _view_model_to_dict(src, dst):
    for key, value in src.items():
        dst[key] = _view_model_to_dict(value, {}) \
            if isinstance(value, dict) else value.get()
    return dst

config_view_model = _dict_to_view_model(config, {})

def register_vm_updates(on_update, *vars_):
    traces = []
    for v in vars_:
        traces.append(
            (v, "write", v.trace_add("write", lambda *a: on_update(v)))
        )
    return traces

def unregister_vm_updates(vm_traces):
    while vm_traces: 
        t = vm_traces.pop(0)
        t[0].trace_remove(t[1], t[2])

def save_data():
    d = _view_model_to_dict(config_view_model, {})
    with open(CONFIG_PATH, 'w') as yaml_file:
        dump(d, yaml_file, sort_keys=False)