# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import ast
from collections import deque
from os import walk
import os.path
from collections.abc import Generator


class IdentVisitor:
    def __init__(self, path: str, ident: str):
        super(IdentVisitor, self).__init__()
        self.path = path
        self.ident = ident.split(".")
        self.attrs = deque()
        self.context = deque()
        self.importMap = {}

    def visit(self, node: ast.AST) -> Generator[tuple, None, None]:
        """Visit a node."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        yield from visitor(node)

    def generic_visit(self, node) -> Generator[tuple, None, None]:
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        yield from self.visit(item)
            elif isinstance(value, ast.AST):
                yield from self.visit(value)

    def visit_ImportFrom(self, node):
        if node.level != 0:
            # relative imports not supported
            # also, ensure we're a generator
            yield from []
            return
        mods = tuple(node.module.split("."))
        for left, right in zip(mods, self.ident):
            if left != right:
                return
        subident = self.ident[len(mods) :]
        for alias in node.names:
            for left, right in zip(alias.name.split("."), subident):
                if left != right:
                    continue
            lname = alias.asname is not None and alias.asname or alias.name
            self.importMap[lname] = mods + (alias.name,)

    def context_visit(self, node):
        self.context.append((node.name, node.lineno))
        yield from self.generic_visit(node)
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
        yield (self.path, self.context, node, ident)

    def visit_Attribute(self, node):
        self.attrs.appendleft(node.attr)
        yield from self.generic_visit(node)


class FindIdentifier:
    def __init__(self, ident, files_or_dirs):
        self.ident = ident
        self.files_or_dirs = files_or_dirs

    def __call__(self) -> Generator[tuple, None]:
        for fd in self.files_or_dirs:
            if os.path.isdir(fd):
                for dirpath, dirnames, filenames in walk(fd):
                    for fn in filenames:
                        if fn.endswith(".py"):
                            yield from self.handleFile(os.path.join(dirpath, fn))
            else:
                yield from self.handleFile(fd)

    def handleFile(self, path):
        m = ast.parse(open(path).read(), path)
        iv = IdentVisitor(path, self.ident)
        yield from iv.visit(m)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--list", action="store_true", help="only gather the list of entrypoints"
    )
    parser.add_argument("ident")
    parser.add_argument("path", nargs="+")

    args = parser.parse_args()
    finder = FindIdentifier(args.ident, args.path)

    if args.list:
        entrypoints = set()
        for _, _, _, ident in finder():
            entrypoints.add(".".join(ident))
        print("\n".join(sorted(entrypoints)))
        return

    for path, context, node, ident in finder():
        fd = ""
        if context:
            fd = "(%s)" % ".".join([t[0] for t in context])
        print("%s%s:%s\t%s" % (path, fd, node.lineno, ".".join(ident)))
