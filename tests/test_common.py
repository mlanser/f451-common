"""Test cases for f451 Labs Common module."""

import pytest
from pathlib import Path

import src.f451_common.common as common


# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return "Hello world"


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_debug(capsys, valid_str):
    print(valid_str)
    captured = capsys.readouterr()
    assert captured.out == "Hello world\n"


def test_load_settings():
    APP_DIR = Path(__file__).parent         # Find dir for this app
    settings = common.load_settings(APP_DIR.joinpath("test.toml"))
    assert settings.get("FOO") == "bar"


def test_get_RPI_ID():
    val = common.get_RPI_ID("prefix-", "-suffix", "default")
    assert val == "default"


def test_num_to_range():
    val = common.num_to_range(10, (0, 100), (0, 100))
    assert val == 10.0

    val = common.num_to_range(10, (0, 100), (0, 10))
    assert val == 1.0


def test_convert_to_bool():
    assert common.convert_to_bool(True)

    assert common.convert_to_bool(1)
    assert common.convert_to_bool(-1)
    assert common.convert_to_bool(1.1)

    assert common.convert_to_bool(common.STATUS_ON)
    assert common.convert_to_bool(common.STATUS_YES)
    assert common.convert_to_bool(common.STATUS_TRUE)


def test_convert_to_bool_fail():
    assert not common.convert_to_bool(False)

    assert not common.convert_to_bool(0.1)
    assert not common.convert_to_bool(-0.1)
    assert not common.convert_to_bool("ok")
    assert not common.convert_to_bool(common.STATUS_UNKNOWN)

    assert not common.convert_to_bool([True])
    assert not common.convert_to_bool((0,0))
    assert not common.convert_to_bool({"foo":"bar"})
