import typing as t
import re
import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--independent",
        action="store_true",
        help="",
    )
    parser.addoption(
        "--depend",
        action="append",
        metavar="DEPENDENCE",
        nargs="+",
        default=[],
        help="",
    )


REGEX_REQUIRE_PEEFIX = re.compile("^require_")


def pytest_runtest_setup(item: pytest.Item):
    required = set(
        re.sub(REGEX_REQUIRE_PEEFIX, "", marker.name)
        for marker in item.iter_markers()
        if marker.name.startswith("require_")
    )

    if item.config.getoption("--independent"):
        dependence = _get_option_depend(item.config)
        if not required <= dependence:
            pytest.skip(f"test requires {required - dependence}")


def _get_option_depend(config: pytest.Config) -> t.Set[str]:
    return set(*config.getoption("--depend"))
