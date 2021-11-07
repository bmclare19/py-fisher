from wrappers.logging_wrapper import debug

_factory_types = ['float', 'int']

def _float_validator(action, index, value_if_allowed,\
    prior_value, text, validation_type, trigger_type, \
        widget_name):
    if value_if_allowed:
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False
    elif value_if_allowed == "":
        return True
    else:
        return False

def _int_validator(action, index, value_if_allowed,\
    prior_value, text, validation_type, trigger_type, \
        widget_name):
    if value_if_allowed:
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False
    elif value_if_allowed == "":
        return True
    else:
        return False

def vcmd_factory(widget, type_):

    assert isinstance(type_, str) and type_.lower() in _factory_types,\
        "type_ must be provided and be a valid option"

    if type_.lower() == "float":
        return (
            widget.register(_float_validator),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
        )
    
    if type_.lower() == "int":
        return (
            widget.register(_int_validator),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
        )

    raise ValueError(
        "Invalid validator type: %s" % type_
        )