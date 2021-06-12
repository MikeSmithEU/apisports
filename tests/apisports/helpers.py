import code


def debugger(**kwargs):
    code.interact(
        banner='Ctrl+D to continue. Available vars: %s' % (', '.join(kwargs.keys())),
        local=kwargs
    )
