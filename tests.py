import pytest
import sys
import typing
from typeduck import TypeDuck, types_validate


@pytest.mark.parametrize('source, target, result', [
    # Simple matches
    (str, None, False),
    (None, str, False),
    (str, str, True),
    (list, list, True),
    (list, typing.List, True),
    (typing.List, list, True),
    (typing.List[int], list, True),
    (list, typing.List[int], True),
    (str, typing.Any, True),
    (typing.Any, int, True),
    (typing.List, typing.List, True),
    (typing.List[str], typing.List[str], True),
    (typing.Optional[str], typing.Optional[str], True),
    (str, int, False),
    (str, list, False),
    (str, typing.List, False),
    (dict, typing.List, False),
    (typing.List, dict, False),
    (typing.Tuple, typing.List, False),
    (typing.Tuple, typing.Dict, False),
    (typing.Dict, typing.List, False),

    # Simple Optional
    (str, typing.Optional[str], True),
    (str, typing.Union[str, None], True),
    (str, typing.Optional[int], False),
    (typing.Optional[str], typing.Optional[int], False),
    (str, typing.Union[int, None], False),
    (typing.Optional[str], str, False),  # because source may be None
    (typing.Union[str, None], str, False),  # because source may be None

    # Simple Unions
    (typing.Union[str, bytes], str, True),
    (typing.Union[str, int], int, True),
    (str, typing.Union[str, bytes], True),
    (typing.Union[str, bytes], typing.Union[str, int], True),
    (typing.Union[str, bytes], int, False),
    (float, typing.Union[str, bytes], False),
    (typing.Union[str, bytes], typing.Union[float, int], False),

    # Objects
    (typing.List[str], typing.Optional[typing.List[str]], True),
    (typing.List[typing.Union[str, int]], typing.List[int], True),
    (typing.List[int], typing.List[typing.Union[str, int]], True),
    (typing.List[str], typing.Optional[typing.List[typing.Union[str, bytes]]], True),
    (typing.List[str], typing.List[int], False),
    (typing.List[typing.Union[str, int]], typing.List[float], False),
    (typing.List[str], typing.List[typing.Union[int, float]], False),
    (str, typing.Optional[typing.List[typing.Union[str, bytes]]], False),
    (typing.List[str], typing.Optional[typing.List[typing.Union[int, bytes]]], False),

    (typing.Dict[str, int], typing.Dict, True),
    (typing.Dict, typing.Dict[str, typing.Any], True),
    (typing.Dict[str, int], typing.Dict[str, typing.Any], True),
    (typing.Dict[str, typing.Any], typing.Dict[str, int], True),
    (typing.Dict[str, int], typing.Dict[int, typing.Any], False),
    (typing.Dict[int, typing.Any], typing.Dict[str, int], False),
])
def test_validate(source, target, result):
    td = TypeDuck(source, target)
    if result:
        assert td.validate() is result
    else:
        with pytest.raises(TypeError):
            td.validate(raises=True)


def test_type_validate():
    with pytest.raises(TypeError):
        types_validate(typing.List[str], typing.Dict, raises=True)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
@pytest.mark.parametrize('f', [
    # wrapped in lambdas to avoid runtime syntax errors
    lambda: (str | bytes, str, True),
    lambda: (int, str | bytes, False),
    lambda: (list[int], list, True),
    lambda: (list, list[str | int], True),
    lambda: (list[int], list[str | int], True),
    lambda: (list[int], typing.List[typing.Union[str, int]], True),
    lambda: (typing.List[int], list[str | int], True),
    lambda: (list[int], list[str | bytes], False),
    lambda: (list[int], typing.List[str | bytes], False),
    lambda: (typing.Any, int | str | None, True),
    lambda: (int | str | None, typing.Any, True),
])
def test_types_validate_py310(f):
    source, target, result = f()
    assert types_validate(source, target) is result
