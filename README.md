typeduck
===

# Introduction

A lightweight utility for comparing annotation declarations for their compatibility.

# Installation

Requires Python 3.8 or above.

```bash
pip install typeduck
```

# Usage

```python
from typing import Union, List
from typeduck import types_validate

source = List[str]
target = List[Union[str, int]]

types_validate(source, target)  # returns a boolean
# OR
types_validate(source, target, raises=True)  # will raise a TypeError when validation fails
```

# Use Cases

## Validate annotations between functions or classes match

```python
from typing import List, Union
from typeduck import types_validate

def my_func() -> List[str]:
    ...

def your_func(data: List[Union[int, str]]):
    ...

source = my_func.__annotations__['return']
target = your_func.__annotations__['data']

are_compatible = types_validate(source, target)  # True
```

See more examples in the [tests.py](https://github.com/den4uk/typeduck/blob/master/tests.py) file.