import ast
import pytest
import pygrep


@pytest.fixture
def simple_import_from():
    "one - two.three.four"
    return ast.parse(
        """\
from one import two
from one import two as one
two.three.four
one.three.four
"""
    )


@pytest.fixture
def level_import_from():
    "one.two - three.four"
    return ast.parse(
        """\
from one.two import three
from one.two import three as one
three.four
one.four
"""
    )


def test_simple_from_one(simple_import_from):
    v = pygrep.IdentVisitor("one")
    hits = list(v.visit(simple_import_from))
    assert [(n.lineno, ident) for context, n, ident in hits] == [
        (3, ("one", "two", "three", "four")),
        (4, ("one", "two", "three", "four")),
    ]


def test_simple_from_two(simple_import_from):
    v = pygrep.IdentVisitor("two")
    hits = list(v.visit(simple_import_from))
    assert [n.lineno for context, n, ident in hits] == []


def test_level_from_one(level_import_from):
    v = pygrep.IdentVisitor("one")
    hits = list(v.visit(level_import_from))
    assert [(n.lineno, ident) for context, n, ident in hits] == [
        (3, ("one", "two", "three", "four")),
        (4, ("one", "two", "three", "four")),
    ]


def test_level_from_two(level_import_from):
    v = pygrep.IdentVisitor("two")
    hits = list(v.visit(level_import_from))
    assert [n.lineno for context, n, ident in hits] == []
