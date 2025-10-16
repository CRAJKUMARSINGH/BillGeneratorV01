import importlib, pkgutil

def load_plugins(namespace="plugins"):
    plugins = {}
    for _, name, _ in pkgutil.iter_modules([namespace]):
        mod = importlib.import_module(f"{namespace}.{name}")
        if hasattr(mod, "register"):
            plugin = mod.register()
            plugins[name] = plugin
    return plugins