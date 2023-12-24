"""f451 Labs Common Cloud module.

The f451 Labs Cloud module encapsulates the Adafruit IO REST and MQTT client 
classes, the Arduino IoT-API client class, and adds a few more features that are 
commonly used in f451 Labs projects.

TODO:
    - update module demo

Dependencies:
    - random
    - oauthlib
    - tomllib / tomli
    - arduino-iot-client
    - requests-authlib
    - adafruit-io
    - typing-extensions < Python 3.10
    - frozendict
"""

import json
import time
import sys
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from random import randint

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from Adafruit_IO import Client as aioREST, MQTTClient as aioMQTT, Feed as aioFeed
# from Adafruit_IO import RequestError, ThrottlingError

import iot_api_client as ardClient
from iot_api_client.rest import ApiException as ardAPIError
from iot_api_client.configuration import Configuration as ardConfig

__all__ = [
    'AdafruitCloud',
    'AdafruitFeed',
    'AdafruitCloudError',
    'ArduinoCloudError',
    'KWD_AIO_ID',
    'KWD_AIO_KEY',
    'KWD_ARD_ID',
    'KWD_ARD_KEY',
    'KWD_AIO_LOC_ID',
    'KWD_AIO_RWRD_ID',
    'KWD_AIO_RNUM_ID',
]

from rich.pretty import pprint


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_AIO_ID = 'AIO_ID'
KWD_AIO_KEY = 'AIO_KEY'
KWD_AIO_LOC_ID = 'AIO_LOC_ID'
KWD_AIO_RWRD_ID = 'AIO_RWRD_ID'
KWD_AIO_RNUM_ID = 'AIO_RNUM_ID'

KWD_ARD_ID = 'ARD_ID'
KWD_ARD_KEY = 'ARD_KEY'


# =========================================================
#                        H E L P E R S
# =========================================================
class AdafruitCloudError(Exception):
    """Custom exception class for Adafruit IO errors"""

    def __init__(self, errMsg='Adafruit IO client not initiated'):
        super().__init__(errMsg)


class ArduinoCloudError(Exception):
    """Custom exception class for Arduino Cloud errors"""

    def __init__(self, errMsg='Arduino Cloud client not initiated'):
        super().__init__(errMsg)


class CloudService(ABC):
    """Basic cloud service class.

    This class is the base for all cloud service classes. It holds
    some common methods and properties to ensure a basic level of
    compatibility between the service objects.
    """

    def __init__(self, srvID, srvKey, rest=None, mqtt=None, active=False):
        self._ID = srvID
        self._KEY = srvKey
        self._REST = rest
        self._MQTT = mqtt
        self._active = active

    @property
    def is_active(self):
        return self._active

    @abstractmethod
    async def send_data(self, *args, **kwargs):
        pass

    @abstractmethod
    async def receive_data(self, *args, **kwargs):
        pass


class Feed(ABC):
    """Basic data feed class.

    This class is the base for all data feed classes. It holds
    some common methods and properties to ensure a basic level of
    compatibility between the data feed objects.
    """

    def __init__(self, service, feed=None, active=True):
        self._service = service
        self._feed = feed
        self._active = feed is not None and active

    @property
    def is_active(self):
        return self._active

    @abstractmethod
    async def send_data(self, *args, **kwargs):
        pass

    @abstractmethod
    async def receive_data(self, *args, **kwargs):
        pass


# =========================================================
#                   M A I N   C L A S S E S
# =========================================================
class AdafruitCloud(CloudService):
    """Main class for managing Adafruit IO service.

    This class encapsulates the Adafruit IO client and makes it
    easier to upload data to and/or receive data from the service.

    NOTE: attributes follow same naming convention as used
    in the 'settings.toml' file. This makes it possible to pass
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myCloud = Cloud(config)           # Use values from 'config'
        myCloud = Cloud(key=val)          # Use val
        myCloud = Cloud(config, key=val)  # Use values from 'config' and also use 'val'

    Attributes:
        AIO_USERNAME:   Adafruit IO username
        AIO_KEY:        Adafruit IO secret/key

    Methods:
        aio_create_feed:    Create a new Adafruit IO feed
        aio_feed_list:      Get complete list of Adafruit IO feeds
        aio_feed_info:      Get info/metadata for an Adafruit IO feed
        aio_delete_feed:    Delete an existing Adafruit IO feed
        aio_send_data:      Send data to an existing Adafruit IO feed
        aio_receive_data:   Receive data from an existing Adafruit IO feed
    """

    def __init__(self, *args, **kwargs):
        """Initialize cloud service

        Args:
            args:
                User can provide single 'dict' with settings
            kwargs:
                User can provide individual settings as key-value pairs
        """

        # We combine 'args' and 'kwargs' to allow users to provide the entire
        # 'config' object and/or individual settings (which could override
        # values in 'config').
        settings = {**args[0], **kwargs} if args and isinstance(args[0], dict) else kwargs

        active = False
        rest = None
        mqtt = None

        aioID = settings.get(KWD_AIO_ID)
        aioKey = settings.get(KWD_AIO_KEY)

        if aioID and aioKey:
            rest = aioREST(aioID, aioKey)
            mqtt = aioMQTT(aioID, aioKey)
            active = bool(rest) and bool(mqtt)
        super().__init__(aioID, aioKey, rest, mqtt, active)

        self._aioLocID = settings.get(KWD_AIO_LOC_ID)
        self._aioRndWrdID = settings.get(KWD_AIO_RWRD_ID)
        self._aioRndNumID = settings.get(KWD_AIO_RNUM_ID)

    @property
    def aioRandWord(self):
        return self._aioRndWrdID

    @property
    def aioRandNumber(self):
        return self._aioRndNumID

    def create_feed(self, feedName, strict=False):
        """Create Adafruit IO feed

        Args:
            feedName:
                'str' name of new Adafruit IO feed
            strict:
                If 'True' then exception is raised if feed already exists

        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        if not feedName:
            raise AdafruitCloudError("Invalid 'feedName' for Adafruit IO client")

        # TODO: this seems wrong. What is 'aioFeed' ?
        feed = aioFeed(name=feedName)

        if strict:
            feedList = self._REST.feeds()
            nameList = [feed.name for feed in feedList]
            if feedName in nameList:
                raise AdafruitCloudError(f"Adafruit IO already has a feed named '{feedName}'")

        return self._REST.create_feed(feed)

    def feed_list(self):
        """Get Adafruit IO feed info

        Returns:
            List of feeds from Adafruit IO

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        return self._REST.feeds()

    def feed_info(self, feedKey):
        """Get Adafruit IO feed info

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        if not feedKey:
            raise AdafruitCloudError("Invalid 'feedKey' for Adafruit IO client")

        return self._REST.feeds(feedKey)

    def delete_feed(self, feedKey):
        """Delete Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        self._REST.delete_feed(feedKey)

    async def send_data(self, feedKey, dataPt):
        """Send data value to Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
            dataPt:
                'str'|'int'|'float' data point
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        self._REST.send_data(feedKey, dataPt)

    async def receive_data(self, feedKey, raw=False):
        """Receive last data value from Adafruit IO feed

        Args:
            feedKey:
                'str' with Adafruit IO feed key
            raw:
                If 'True' then raw data object (in form
                of 'namedtuple') is returned
        Returns:
            Adafruit feed info

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        data = self._REST.receive(feedKey)
        return data if raw else data.value

    async def receive_weather(self, weatherID=None, raw=False):
        """Receive weather data from Adafruit IO feed

        Args:
            weatherID:
                'int' with Adafruit IO weather ID
            raw:
                If 'True' then raw data object (in form
                of 'namedtuple') is returned, else data
                is returned as JSON
        Returns:
            Adafruit weather data

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        wID = weatherID if weatherID is not None else self._aioLocID
        data = self._REST.receive_weather(wID)
        return data if raw else json.loads(json.dumps(data))

    async def receive_random(self, randomID=None, raw=False):
        """Receive random value from Adafruit IO feed

        Args:
            randomID:
                'int' with Adafruit IO random generator ID
            raw:
                If 'True' then raw data object (in form
                of 'namedtuple') is returned, else data
                is returned as JSON
        Returns:
            Adafruit random data

        Raises:
            CloudError:
                When Adafruit IO client is not initiated
            RequestError:
                When API request fails
            ThrottlingError:
                When exceeding Adafruit IO rate limit
        """
        if not self._active:
            raise AdafruitCloudError()

        data = self._REST.receive_random(randomID)
        return data if raw else data.value

    # async def aio_receive_random_word(self):
    #     return asyncio.run(self.aio_receive_random(self._aioRndWrdID))

    # async def aio_receive_random_number(self):
    #     return asyncio.run(self.aio_receive_random(self._aioRndNumID))


class AdafruitFeed(Feed):
    """Adafruit IO Feed class
    
    This wrapper calss allows us to standardize function
    signatures for similar features across cloud services.
    """
    def __init__(self, service, feed, active=True):
        super().__init__(service, feed, active)

    async def send_data(self, dataPt):
        if not self._active:
            raise AdafruitCloudError('Adafruit IO feed not active')

        await self._service.send_data(self._feed.key, dataPt)

    async def receive_data(self, raw=False):
        if not self._active:
            raise AdafruitCloudError('Adafruit IO feed not active')

        return self._service.receive_data(self._feed.key, raw)


class ArduinoCloud(CloudService):
    """Main Cloud class for managing IoT data uploads.

    This class encapsulates the Arduino Cloud client and makes it
    easier to upload data to and/or receive data from the service.

    NOTE: attributes follow same naming convention as used
    in the 'settings.toml' file. This makes it possible to pass
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myCloud = Cloud(config)           # Use values from 'config'
        myCloud = Cloud(key=val)          # Use val
        myCloud = Cloud(config, key=val)  # Use values from 'config' and also use 'val'


    * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    *    TODO: THIS CLASS IS STILL WORK IN PROGRESS -- DO NOT USE AS IS!    *
    * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

    Attributes:
        ARD_USERNAME:   Arduino Cloud client ID
        ARD_KEY:        Arduino Cloud secret/key

    Methods:
        ???
    """

    def __init__(self, *args, **kwargs):
        """Initialize Cloud

        Args:
            args:
                User can provide single 'dict' with settings
            kwargs:
                User can provide individual settings as key-value pairs
        """

        # We combine 'args' and 'kwargs' to allow users to provide the entire
        # 'config' object and/or individual settings (which could override
        # values in 'config').
        settings = {**args[0], **kwargs} if args and isinstance(args[0], dict) else kwargs

        active = False
        ard = None

        ardID = settings.get(KWD_ARD_ID)
        ardKey = settings.get(KWD_ARD_KEY)

        if ardID and ardKey:
            ard = None  # TO DO: fix this placeholder
            active = bool(ard)

        super().__init__(ardID, ardKey, ard, None, active)


# =========================================================
#                    M O D U L E   D E M O
# =========================================================
if __name__ == '__main__':
    # Initialize TOML parser and try to load 'settings.toml' file
    try:
        with open(Path(__file__).parent.joinpath('settings.toml'), mode='rb') as fp:
            config = tomllib.load(fp)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        config = {
            'AIO_ID': None,  # Set your 'ADAFRUIT IO USERNAME'
            'AIO_KEY': None,  # set your 'ADAFRUIT IO KEY'
            'AIO_LOC_ID': None,  # set your 'ADAFRUIT IO Weather Location ID'
        }

    # Check for creds
    if not config.get('AIO_ID') or not config.get('AIO_KEY'):
        sys.exit('ERROR: Missing Adafruit IO credentials')

    AIO = AdafruitCloud(config)
    feedName = f'TEST_FEED_{str(time.time_ns())}'

    print('\n===== [Demo of f451 Labs Cloud Module] =====')
    print(f'Creating new Adafruit IO feed: {feedName}')
    feed = AIO.create_feed(feedName)

    dataPt = randint(1, 100)
    print(f"Uploading random value '{dataPt}' to Adafruit IO feed: {feed.key}")
    asyncio.run(AIO.send_data(feed.key, dataPt))

    print(f'Receiving latest from Adafruit IO feed: {feed.key}')
    data = asyncio.run(AIO.receive_data(feed.key, True))

    # Adafruit IO returns data in form of 'namedtuple' and we can
    # use the '_asdict()' method to convert it to regular 'dict'.
    # We then pass the 'dict' to 'json.dumps()' to prettify before
    # we print out the whole structure.
    pretty = json.dumps(data._asdict(), indent=4, sort_keys=True)
    print(pretty)

    # Get weather forecast from Adafruit IO as JSON
    print('\n--------------------------------------------')
    print('Receiving latest weather data from Adafruit IO')
    forecast = asyncio.run(AIO.receive_weather())
    print(json.dumps(forecast, indent=4, sort_keys=True))

    # Parse the current forecast
    # current = forecast['current']
    # print("Current Forecast")
    # print(f"It's {current['conditionCode']} and {current['temperature']}C")

    # Parse 2-day forecast
    # forecast2d = forecast['forecast_days_2']
    # print("\nWeather in Two Days")
    # print(f"It'll be {forecast2d['conditionCode']} with a high of {forecast2d['temperatureMin']}C and a low of {forecast2d['temperatureMax']}C.")

    # Parse the five day forecast
    # forecast5d = forecast['forecast_days_5']
    # print('\nWeather in Five Days')
    # print(f"It'll be {forecast5d['conditionCode']} with a high of {forecast5d['temperatureMin']}C and a low of {forecast5d['temperatureMax']}C.")

    # Get random data from Adafruit IO
    print('\n--------------------------------------------')
    # someWord = asyncio.run(iot.aio_receive_random_word())
    # print(f"Receiving random word from Adafruit IO: {someWord}")
    print('Receiving random word from Adafruit IO')
    someWord = asyncio.run(AIO.receive_random(AIO.aioRandWord, True))
    print(json.dumps(someWord, indent=4, sort_keys=True))

    print('\n--------------------------------------------')
    # someNumber = asyncio.run(iot.aio_receive_random_number())
    # print(f"Receiving random number from Adafruit IO: {someNumber}")
    print('Receiving random number from Adafruit IO')
    someNumber = asyncio.run(AIO.receive_random(AIO.aioRandNumber, True))
    print(json.dumps(someNumber, indent=4, sort_keys=True))

    print('=============== [End of Demo] =================\n')
