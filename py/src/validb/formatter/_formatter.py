import string
import typing as t


class MessageFormatter(string.Formatter):
    """Formatter with no error if key not found"""

    def get_value(
        self,
        key: t.Union[int, str],
        args: t.Sequence[t.Any],
        kwargs: t.Mapping[str, t.Any],
    ) -> t.Any:
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError):
            return ""
