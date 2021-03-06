# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import ast
from collections import deque
from os import walk
import os.path
from six.moves import zip


class IdentVisitor(ast.NodeVisitor):
    def __init__(self, path, ident, callback):
        super(IdentVisitor, self).__init__()
        self.path = path
        self.ident = ident.split('.')
        self.callback = callback
        self.attrs = deque()
        self.context = deque()
        self.importMap = {}

    def visit_ImportFrom(self, node):
        if node.level != 0:
            # relative imports not supported
            return
        mods = tuple(node.module.split('.'))
        for left, right in zip(mods, self.ident):
            if left != right:
                return
        subident = self.ident[len(mods):]
        for alias in node.names:
            for left, right in zip(alias.name.split('.'), subident):
                if left != right:
                    continue
            lname = alias.asname is not None and alias.asname or alias.name
            self.importMap[lname] = mods + (alias.name, )

    def context_visit(self, node):
        self.context.append((node.name, node.lineno))
        self.generic_visit(node)
        self.context.pop()
    visit_FunctionDef = visit_ClassDef = context_visit

    def visit_Name(self, node):
        ident = tuple(self.attrs) + (node.id,)
        self.attrs.clear()
        if ident[0] in self.importMap:
            ident = self.importMap[ident[0]] + ident[1:]
        if len(ident) < len(self.ident):
            return
        for left, right in zip(ident, self.ident):
            if left != right:
                return
        self.callback(self.path, self.context, node, ident)

    def visit_Attribute(self, node):
        self.attrs.appendleft(node.attr)
        self.generic_visit(node)


class handleIdent:
    def __init__(self, ident, files_or_dirs, callback):
        self.ident = ident
        self.callback = callback
        for fd in files_or_dirs:
            if os.path.isdir(fd):
                for dirpath, dirnames, filenames in walk(fd):
                    for fn in filenames:
                        if fn.endswith('.py'):
                            self.handleFile(os.path.join(dirpath, fn))
            else:
                self.handleFile(fd)

    def handleFile(self, path):
        m = ast.parse(open(path).read(), path)
        iv = IdentVisitor(path, self.ident, self.callback)
        iv.visit(m)
