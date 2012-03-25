Ever tried to refactor some python code and trying to find out where you're
code is used?

    find . -name \*.py | xargs grep foo.bar

is kinda nice, but it'll find imports, comments, and whatnot.

Meet pygrep, it allows you to find all references to your code,

    pygrep foo.bar some/dir other/stuff.py

That will show you some output like

    file.py(Class.function):lineno foo.bar.full.identifier

In `file.py`, there's a reference to `foo.bar.full.identifier` in the method
`function` in class `Class`.

Supported
---------
At this point, pygrep resolves

    from foo import bar

and

    from foo import bar as baz

Example
-------

Given this python file `foo.py`

    from mymod.bar import stuff as a
    class A:
        def m(self):
            b = a.mod.method()

all the following commands

    pygrep mymod foo.py
    pygrep mymod.bar foo.py
    pygrep mymod.bar.mod foo.py
    pygrep mymod.bar.mod.method foo.py

will return

    foo.py(A.m):4 mymod.bar.mod.method
