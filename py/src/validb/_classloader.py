import importlib
import typing as t

T = t.TypeVar("T")


class IllegalPathError(ValueError):
    def __init__(self, actual_path: t.Any) -> None:
        super().__init__(
            f"class name must be a string like 'module.class', but the actual name is {actual_path}"
        )
        self.actual_path = actual_path


class NonClassLoadedError(TypeError):
    def __init__(self, actual_loaded: t.Any) -> None:
        super().__init__(
            f"loaded object must be class, but the actual type is {type(actual_loaded).__name__}"
        )
        self.actual_loaded = actual_loaded


class UnexpectedClassLoadedError(TypeError):
    def __init__(
        self, actual_loaded: t.Type[t.Any], expected_class: t.Type[t.Any]
    ) -> None:
        super().__init__(
            f"loaded class must be subclass of {expected_class.__name__}, but the actual class is {actual_loaded.__name__}"
        )
        self.actual_loaded = actual_loaded


def import_class_dinamically(
    path: t.Any,
    *,
    expected_class: t.Type[T],
) -> t.Type[T]:
    """import class dinamically

    Parameters
    ----------
    path : str
        The pass of class. Include module name.
    expected_class : Type
        The class expected.
        The class to be imported here is required to be a subclass of this class.

    Returns
    -------
    Type
        The class imported

    Raises
    ------
    IllegalPathError
        Illegal class name was specified.
    NonClassLoadedError
        A non-class object loaded.
    UnexpectedClassLoadedError
        A class different from the one specified was loaded.
    ModuleNotFoundError
        The specified module does not exist.
    AttributeError
        The specified class does not exist in the specified module.
    """
    if not isinstance(path, str):
        raise IllegalPathError(path)

    path_parts = path.split(".")
    if len(path_parts) < 2:
        raise IllegalPathError(path)

    module_str = ".".join(path_parts[:-1])
    class_name = path_parts[-1]
    module = importlib.import_module(module_str)

    class_loaded: t.Type[t.Any] = getattr(module, class_name)

    if not isinstance(class_loaded, t.Type):
        raise NonClassLoadedError(class_loaded)
    if not issubclass(class_loaded, expected_class):
        raise UnexpectedClassLoadedError(class_loaded, expected_class=expected_class)

    return class_loaded


def construct_imported_dinamically(
    attr: t.Mapping[str, t.Any],
    expected_class: t.Type[T],
) -> T:
    class_loaded = import_class_dinamically(
        attr["class"], expected_class=expected_class
    )
    instance = class_loaded(
        **{key: value for key, value in attr.items() if key != "class"}
    )
    return instance
