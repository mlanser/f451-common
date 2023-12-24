"""Test cases for f451 Labs Common Cloud module.

Some of these test cases will send data to and/or receive 
data from Adafruit IO and Arduino Cloud services. These 
tests require the presence of valid account IDs and secrets 
in the 'settings.toml' file.
"""

import pytest
import time
import asyncio
from pathlib import Path
from random import randint

from src.f451_common.cloud import AdafruitCloud

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
KWD_TST_VAL = 'TST_VAL'
DEF_TST_VAL = 'test1-2-3'


# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return 'Hello world'


@pytest.fixture(scope='session')
def config():
    settings = 'src/f451_common/settings.toml'
    try:
        with open(Path(__file__).parent.parent.joinpath(settings), mode='rb') as fp:
            config = tomllib.load(fp)
    except tomllib.TOMLDecodeError:
        pytest.fail("Invalid 'settings.toml' file")
    except FileNotFoundError:
        pytest.fail("Missing 'settings.toml' file")

    return config


@pytest.fixture(scope='session')
def cloud(config):
    return AdafruitCloud(config)


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_dummy(valid_str):
    """Dummy test case.

    This is only a placeholder test case.
    """
    assert valid_str == 'Hello world'


def test_config(config):
    setting = config[KWD_TST_VAL]

    assert setting == DEF_TST_VAL


def test_init_aio(config):
    cloud = AdafruitCloud(config)

    assert cloud.is_active


@pytest.mark.online
@pytest.mark.adafruit
def test_aio_create_and_delete_feed(cloud):
    #
    # NOTE: This test requires active Adafruit IO account.
    #
    feedName = f'TEST-FEED-{str(time.time_ns())}'

    feedInfo = cloud.create_feed(feedName)
    feedList = cloud.feed_list()
    nameList = [feed.name for feed in feedList]
    assert feedName in nameList

    cloud.delete_feed(feedInfo.key)
    feedList = cloud.feed_list()
    nameList = [feed.name for feed in feedList]
    assert feedName not in nameList


@pytest.mark.online
@pytest.mark.adafruit
def test_aio_send_and_delete_data(cloud):
    #
    # NOTE: This test requires active Adafruit IO account.
    #
    feedName = f'TEST-FEED-{str(time.time_ns())}'
    dataPt = randint(1, 100)

    feedInfo = cloud.create_feed(feedName)
    asyncio.run(cloud.send_data(feedInfo.key, dataPt))
    checkData = asyncio.run(cloud.receive_data(feedInfo.key))
    cloud.delete_feed(feedInfo.key)
    assert int(checkData) == dataPt
