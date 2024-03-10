import importlib
import typing as t

T = t.TypeVar("T")


class IllegalPathError(ValueError):
    def __init__(self, actual_path: t.Any, *args: object) -> None:
        super().__init__(actual_path, *args)
        self.actual_path = actual_path


class UnexpectedClassLoadedError(TypeError):
    def __init__(self, actual_class: t.Type[t.Any], *args: object) -> None:
        super().__init__(actual_class, *args)
        self.actual_class = actual_class


def import_class_dinamically(
    path: t.Any,
    *,
    module_cached: t.Optional[t.MutableMapping[str, t.Type[t.Any]]] = None,
    expected_class: t.Type[T],
) -> t.Type[T]:
    # TODO: use module_cached

    if not isinstance(path, str):
        raise IllegalPathError(path)

    path_parts = path.split(".")
    if len(path_parts) < 2:
        raise IllegalPathError(path)

    module_str = ".".join(path_parts[:-1])
    class_name = path_parts[-1]
    module = importlib.import_module(module_str)

    class_loaded = getattr(module, class_name)

    if not issubclass(class_loaded, expected_class):
        raise UnexpectedClassLoadedError(class_loaded)

    if module_cached is not None:
        module_cached[path] = class_loaded
    return class_loaded


def construct_imported_dinamically(
    attr: t.Mapping[str, t.Any],
    expected_class: t.Type[T],
    *,
    module_cached: t.Optional[t.MutableMapping[str, t.Type[t.Any]]] = None,
) -> T:
    class_loaded = import_class_dinamically(
        attr["class"], expected_class=expected_class, module_cached=module_cached
    )
    instance = class_loaded(
        **{key: value for key, value in attr.items() if key != "class"}
    )
    return instance
