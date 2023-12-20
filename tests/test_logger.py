"""Test cases for f451 Labs Logger module.

These test cases will capture stdout and verify that log 
files are created.

Some tests are based on examples found here:
    https://www.kazis.dev/blogs/pytest-caplog
"""

import pytest
import logging

from src.f451_logger.logger import Logger


# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return 'Hello world'


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_debug(capsys, valid_str):
    logger = Logger()
    logger.debug(valid_str)

    captured = capsys.readouterr()
    assert captured.out == "'Hello world'\n"


def test_log_default(caplog, valid_str):
    caplog.set_level(logging.DEBUG)

    logger = Logger(LOGNAME='testLogger', LOGLVL=logging.DEBUG)
    logger.log(valid_str)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == 'DEBUG'
    assert caplog.records[0].name == 'testLogger'

    caplog.clear()
    caplog.set_level(logging.DEBUG + 5)

    logger.log_debug(valid_str)

    assert not caplog.text
    assert not caplog.records


@pytest.mark.parametrize(
    'testLogLvl, testLogLvlStr',
    [
        (logging.DEBUG, 'DEBUG'),
        (logging.INFO, 'INFO'),
        (logging.WARNING, 'WARNING'),
        (logging.ERROR, 'ERROR'),
    ],
)
def test_log(caplog, valid_str, testLogLvl, testLogLvlStr):
    caplog.set_level(logging.DEBUG)

    logger = Logger(LOGNAME='testLogger', LOGLVL=testLogLvl)
    logger.log(valid_str, testLogLvl)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == testLogLvlStr

    caplog.clear()
    caplog.set_level(testLogLvl + 5)

    logger.log(valid_str, testLogLvl)

    assert not caplog.text
    assert not caplog.records


def test_log_debug(caplog, valid_str):
    caplog.set_level(logging.DEBUG)

    logger = Logger(LOGNAME='testLogger', LOGLVL=logging.DEBUG)
    logger.log_debug(valid_str)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == 'DEBUG'
    assert caplog.records[0].name == 'testLogger'

    caplog.clear()
    caplog.set_level(logging.DEBUG + 5)

    logger.log_debug(valid_str)

    assert not caplog.text
    assert not caplog.records


def test_log_info(caplog, valid_str):
    caplog.set_level(logging.INFO)

    logger = Logger(LOGNAME='testLogger', LOGLVL=logging.INFO)
    logger.log_info(valid_str)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].name == 'testLogger'

    caplog.clear()
    caplog.set_level(logging.INFO + 5)

    logger.log_info(valid_str)

    assert not caplog.text
    assert not caplog.records


def test_log_warning(caplog, valid_str):
    caplog.set_level(logging.WARNING)

    logger = Logger(LOGNAME='testLogger', LOGLVL=logging.WARNING)
    logger.log_warning(valid_str)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].name == 'testLogger'

    caplog.clear()
    caplog.set_level(logging.WARNING + 5)

    logger.log_warning(valid_str)

    assert not caplog.text
    assert not caplog.records


def test_log_error(caplog, valid_str):
    caplog.set_level(logging.ERROR)

    logger = Logger(LOGNAME='testLogger', LOGLVL=logging.ERROR)
    logger.log_error(valid_str)

    assert valid_str in caplog.text
    assert caplog.records[0].levelname == 'ERROR'
    assert caplog.records[0].name == 'testLogger'

    caplog.clear()
    caplog.set_level(logging.ERROR + 5)

    logger.log_error(valid_str)

    assert not caplog.text
    assert not caplog.records
