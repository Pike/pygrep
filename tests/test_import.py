import ast
import pytest
import pygrep


@pytest.fixture
def simple_import():
    "one - two.three.four"
    return ast.parse(
        """\
import one.two
import one.two as other
one.two.three.four
other.three.four
"""
    )


def test_simple_one(simple_import):
    v = pygrep.IdentVisitor("one")
    hits = list(v.visit(simple_import))
    assert [(n.lineno, ident) for context, n, ident in hits] == [
        (3, ("one", "two", "three", "four")),
        (4, ("one", "two", "three", "four")),
    ]


def test_simple_two(simple_import):
    v = pygrep.IdentVisitor("other")
    hits = list(v.visit(simple_import))
    assert [n.lineno for context, n, ident in hits] == []
