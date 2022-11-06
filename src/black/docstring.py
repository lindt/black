from os import linesep
from enum import Enum
import black
from black.parsing import InvalidInput


def format(value, line, column, mode):
    """
    >>> import black
    >>> def test(*values, line=0, column=0):
    ...     print(
    ...         "$"
    ...         + f"{linesep}$".join(
    ...             format(
    ...                 linesep.join(values),
    ...                 line=line,
    ...                 column=column,
    ...                 mode=black.mode.Mode(string_normalization=False),
    ...             ).splitlines()
    ...         )
    ...     )
    >>> test(">>> print('test')")
    $>>> print('test')
    >>> test(
    ...     "ordinary documentation",
    ...     ">>> print('test')",
    ... )
    $ordinary documentation
    $>>> print('test')
    >>> test(
    ...     ">>> print('test')",
    ...     column=6,
    ... )
    $      >>> print('test')
    >>> test("ordinary documentation")
    $ordinary documentation
    >>> test(">>>  print('test')")
    $>>> print('test')
    >>> test(">>>  1   + 2")
    $>>> 1 + 2
    >>> test(
    ...     ">>>    a=23",
    ...     ">>>    b   =    42",
    ... )
    $>>> a = 23
    $>>> b = 42
    >>> test(
    ...     ">>> def foo(  ):",
    ...     "...    a   =    23",
    ...     "...    b =         42",
    ... )
    $>>> def foo():
    $...     a = 23
    $...     b = 42

    Examples with broken doctests:
    >>> test(
    ...     ">>> ('non terminated parenthesis'",
    ...     line=23,
    ...     column=42,
    ... )  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    black.parsing.InvalidInput: Cannot parse code within doctest: 23:42:  ('non terminated parenthesis'
    >>> test(
    ...     ">>> a=1",
    ...     "... b=2",
    ...     line=23,
    ...     column=42,
    ... )  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    black.parsing.InvalidInput: Cannot parse code within doctest: 23:42:  a=1
     b=2
    >>> test(
    ...     "... starting_with_code_continuation=2",
    ...     line=23,
    ...     column=42,
    ... )
    $... starting_with_code_continuation=2
    """
    State = Enum("State", "documentation code")

    def iterate(value):
        state, lines = None, []
        for line in value.split(linesep):
            is_code_line = line.lstrip().startswith(">>>")
            if state is None:
                state = State.code if is_code_line else State.documentation
            elif state == State.documentation:
                if is_code_line:
                    yield (state, lines)
                    lines = []
                    state = State.code
            elif state == State.code:
                if not (_is_code_continuation := line.lstrip().startswith("...")):
                    yield (state, lines)
                    lines = []
                    state = State.code if is_code_line else State.documentation
            else:
                assert False

            lines.append(line)
        yield (state, lines)

    def format_by_block(blocks):
        def strip_doctest(code):
            for line in code.splitlines():
                yield line.lstrip(" ").lstrip(">>>").lstrip("...")

        def join_doctest(code):
            for i, line in enumerate(code.split(linesep)):
                yield " " * column + (">>>" if i == 0 else "...") + (
                    line if line == "" else f" {line}"
                )

        def format_code(code):
            try:
                result = linesep.join(code)

                return black.format_str(result, mode=mode).rstrip(linesep)
            except InvalidInput as exception:
                raise InvalidInput(
                    f"Cannot parse code within doctest: {line}:{column}: {result}{linesep}"
                ) from exception

        for state, lines in iterate(blocks):
            if state is State.code:
                yield join_doctest(format_code(strip_doctest(linesep.join(lines))))
                continue

            yield lines

    return linesep.join(linesep.join(lines) for lines in format_by_block(value))
