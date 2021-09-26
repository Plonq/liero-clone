observers = {}


def observe(name, callback):
    if name not in observers:
        observers[name] = []
    observers[name].append(callback)


def emit_event(name, *args, **kwargs):
    if name in observers:
        for callback in observers[name]:
            callback(*args, **kwargs)
