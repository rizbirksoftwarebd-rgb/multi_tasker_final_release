import importlib, pkgutil, pages, inspect
from db import register_page

def discover_pages():
    discovered = []
    package = pages
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"pages.{name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__ and obj.__name__ == 'Page':
                title = getattr(obj, 'title', name.title())
                discovered.append({'module': f'pages.{name}', 'name': name, 'title': title})
                try:
                    register_page(name, title)
                except Exception:
                    pass
    return discovered
