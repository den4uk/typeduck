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
from typeduck import TypeDuck

source = List[str]
target = List[Union[str, int]]

td = TypeDuck(source, target)

td.validate()  # returns a boolean when validation passes
# OR
td.validate(raises=True)  # will raise a TypeError when validation fails
```

See more examples in the [tests.py](https://github.com/den4uk/typeduck/blob/master/tests.py) file.