import types
import typing
import itertools
import contextlib
from dataclasses import dataclass, field


@dataclass
class TypeDuck:
    """
    Checks annotation types for validity between typing annotations, without instances.
    """
    source: typing.Any
    target: typing.Any

    def validate(self, raises: bool = False) -> bool:
        """
        Validates the combination of annotations for their compatibility.

        Args:
            source: annotation value that is an input for the target
            target: annotation value to compatibility with the source

        Returns:
            bool: when the source and target match

        Raises:
            TypeError: when mismatch happens; toggled by `raises` argument when set to True
        """
        src = _AnnotationMeta(self.source)
        trg = _AnnotationMeta(self.target)
        try:
            return self._validate(src, trg)
        except TypeError as exc:
            if raises:
                raise TypeError(f'{self.source} does not validate with {self.target}') from exc
            return False

    @classmethod
    def _validate(cls, src, trg, **kwargs) -> bool:
        return (
            cls._validate_simple_matches(src, trg, **kwargs)
            or cls._validate_with_optionals(src, trg, **kwargs)
            or cls._validate_with_unions(src, trg, **kwargs)
            or cls._validate_objects(src, trg, **kwargs)
            or cls._validation_failed()
        )

    @classmethod
    def _validate_simple_matches(cls, src, trg, **kwargs) -> bool:
        return any([
            all([src.t == trg.t, not src.is_optional]),
            all([src.t == trg.t, src.is_optional, trg.is_optional]),
            src.is_any or trg.is_any,
        ])

    @classmethod
    def _validate_with_optionals(cls, src, trg, **kwargs) -> bool:
        modified = False
        if src.is_optional and src.is_union and src.children:
            modified = src = src.children[0]
            src.is_optional = True
        if trg.is_optional and trg.is_union and trg.children:
            modified = trg = trg.children[0]
        if modified:
            return cls._validate(src, trg, **kwargs)
        return False

    @classmethod
    def _validate_with_unions(cls, src, trg, **kwargs) -> bool:
        has_unions = any([
           all([src.is_union, not src.is_optional, src.children]),
           all([trg.is_union, not trg.is_optional, trg.children])
        ])
        if has_unions:
            for prod in itertools.product(([*src] or [src]), ([*trg] or [trg])):
                with contextlib.suppress(TypeError):
                    return cls._validate(*prod, **kwargs)
        return False

    @classmethod
    def _validate_objects(cls, src, trg, **kwargs) -> bool:
        is_same_object = all([
            src.origin == trg.origin,
            src.is_typing,
            trg.is_typing,
        ])
        has_children = all([
            src.children,
            trg.children
        ])
        if is_same_object:
            if has_children:
                return all(map(lambda x: cls._validate(*x), zip(src, trg)))
            else:
                return True
        return False

    @staticmethod
    def _validation_failed():
        raise TypeError('End of available validations was reached')


@dataclass
class _AnnotationMeta:
    """
    Helper class for categorising annotations
    """
    t: typing.Any

    is_typing: bool = field(default=None, init=False)
    origin: type = field(default=None, init=False)
    is_any: bool = field(default=None, init=False)
    is_union: bool = field(default=None, init=False)
    is_optional: bool = field(default=None, init=False)
    args: typing.Tuple = field(default=None, init=False)
    children: typing.List = field(default_factory=list, init=False)

    _TYPING_GENERIC_TYPES = None
    _BUILTIN_DATA_STRUCTURES_MAP = {
        list: typing.List,
        set: typing.Set,
        dict: typing.Dict,
        tuple: typing.Tuple,
    }

    def __post_init__(self):
        self._is_builtin_data_structure()
        if self._is_typing_class_test():
            if not self._is_any_test():
                self._is_union_test()
                if self._has_args_test():
                    self._is_optional_test()
                    self._process_children()

    @property
    def _typing_generic_types(self):
        if not self._TYPING_GENERIC_TYPES:
            typing_class_names = (
                'GenericAlias', '_GenericAlias',
                '_SpecialForm', '_SpecialGenericAlias',
            )
            types_class_names = (
                'UnionType', 'GenericAlias'
            )
            self._TYPING_GENERIC_TYPES = tuple(
                getattr(typing, name)
                for name in typing_class_names
                if hasattr(typing, name)
            ) + tuple(
                getattr(types, name)
                for name in types_class_names
                if hasattr(types, name)
            )
        return self._TYPING_GENERIC_TYPES

    def _is_builtin_data_structure(self) -> None:
        if typing_match := self._BUILTIN_DATA_STRUCTURES_MAP.get(self.t):
            self.t = typing_match

    def _is_typing_class_test(self) -> bool:
        self.is_typing = isinstance(self.t, self._typing_generic_types)
        return self.is_typing

    def _is_union_test(self) -> bool:
        self.is_union = (self.origin == typing.Union) or (self.t.__class__ == getattr(types, 'UnionType', None))
        return self.is_union

    def _is_optional_test(self) -> bool:
        self.is_optional = self.is_union and self.args and None.__class__ in self.args
        return self.is_optional

    def _is_any_test(self) -> bool:
        self.is_any = self.t == typing.Any
        if not self.is_any:
            self.origin = getattr(self.t, '__origin__', None)
        return self.is_any

    def _has_args_test(self) -> bool:
        if args := getattr(self.t, '__args__', None):
            self.args = tuple(arg for arg in args if not isinstance(arg, typing.TypeVar))
        return bool(self.args)

    def _process_children(self):
        for arg in self.args:
            if not isinstance(arg, None.__class__):
                self.children.append(self.__class__(arg))

    def __iter__(self):
        yield from self.children


def types_validate(source: typing.Any, target: typing.Any, **kwargs: typing.Any) -> bool:
    return TypeDuck(source, target).validate(**kwargs)
