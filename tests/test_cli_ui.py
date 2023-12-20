"""Test cases for f451 Labs CLI UI module."""

import pytest

import src.f451_cli_ui.cli_ui as CLIUI


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
