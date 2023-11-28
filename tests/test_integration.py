import ast
import pytest
import pygrep


@pytest.fixture
def a():
    return ast.parse(
        """\
import ast
import typing

import asyncio

asyncio.create_task
from asyncio import create_task

create_task
from asyncio import create_task as blue

blue



def f():
    import asyncio
    asyncio.create_task
    from asyncio import create_task
    create_task
    from asyncio import create_task as blue
    blue


def main():
    ast.parse(source=__file__, filename=__file__,type_comments=True)


main()
"""
    )


def test_asyncio(a):
    v = pygrep.IdentVisitor("asyncio")
    hits = list(v.visit(a))
    assert [(n.lineno, ident) for context, n, ident in hits] == [
        (6, ("asyncio", "create_task")),
        (9, ("asyncio", "create_task")),
        (12, ("asyncio", "create_task")),
        (18, ("asyncio", "create_task")),
        (20, ("asyncio", "create_task")),
        (22, ("asyncio", "create_task")),
    ]


def test_create_task(a):
    v = pygrep.IdentVisitor("create_task")
    hits = list(v.visit(a))
    assert hits == []
