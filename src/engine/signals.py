observers = {}


def observe(name, callback, source="any"):
    if name not in observers:
        observers[name] = []
    observers[name].append({"source": source, "callback": callback})


def emit_event(name, source="global", *args, **kwargs):
    if name in observers:
        for observer in observers[name]:
            if observer["source"] == "any" or observer["source"] == source:
                observer["callback"](*args, **kwargs)
