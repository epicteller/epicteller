#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError:
        if not silent:
            raise


def load_modules(import_path, include_packages=False, recursive=False):
    for modname in find_modules(import_path, include_packages=include_packages, recursive=recursive):
        if modname:
            import_string(modname)


def find_modules(import_path, include_packages=False, recursive=False):
    """Find all the modules below a package.  This can be useful to
    automatically import all views / controllers so that their metaclasses /
    function decorators have a chance to register themselves on the
    application.

    Packages are not returned unless `include_packages` is `True`.  This can
    also recursively list modules but in that case it will import all the
    packages to get the correct load path of that module.

    :param import_path: the dotted name for the package to find child modules.
    :param include_packages: set to `True` if packages should be returned, too.
    :param recursive: set to `True` if recursion should happen.
    :return: generator
    """
    module = import_string(import_path)
    path = getattr(module, '__path__', None)
    if path is None:
        yield
        return
    basename = module.__name__ + '.'
    for modname, ispkg in _iter_modules(path):
        modname = basename + modname
        if ispkg:
            if include_packages:
                yield modname
            if recursive:
                for item in find_modules(modname, include_packages, True):
                    yield item
        else:
            yield modname


def _iter_modules(path):
    """Iterate over all modules in a package."""
    import os
    import pkgutil
    if hasattr(pkgutil, 'iter_modules'):
        for importer, modname, ispkg in pkgutil.iter_modules(path):
            yield modname, ispkg
        return
    from inspect import getmodulename
    from pydoc import ispackage
    found = set()
    for path in path:
        for filename in os.listdir(path):
            modname = getmodulename(filename)
            if modname and modname != '__init__':
                if modname not in found:
                    found.add(modname)
                    yield modname, ispackage(modname)
