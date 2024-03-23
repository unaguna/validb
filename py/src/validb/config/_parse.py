import typing as t

from .._classloader import construct_imported_dinamically

_T = t.TypeVar("_T")


def parse_object(
    attr: t.Mapping[str, t.Any], path: str, expected_class: t.Type[_T]
) -> _T:
    try:
        return construct_imported_dinamically(attr, expected_class=expected_class)
    except Exception as e:
        raise ParseObjectException(path) from e


class ParseObjectException(Exception):
    def __init__(self, object_path: str) -> None:
        super().__init__(f"failed to parse object {object_path}")
