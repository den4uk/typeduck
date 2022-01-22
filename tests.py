import pytest
import typing
from typeduck import TypeDuck


@pytest.mark.parametrize('source, target, result', [
    # Simple matches
    (str, None, False),
    (None, str, False),
    (str, str, True),
    (str, typing.Any, True),
    (typing.Any, int, True),
    (typing.List, typing.List, True),
    (typing.List[str], typing.List[str], True),
    (typing.Optional[str], typing.Optional[str], True),
    (str, int, False),
    (str, typing.List, False),
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
