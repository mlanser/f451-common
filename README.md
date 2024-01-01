# f451 Labs Common module v2.2.5

## Overview

This module consists of the following core components:

- **CLI UI** — contains functions, variables, and constants that can be used to create common UI elements for *f451 Labs* projects.
- **Cloud** — encapsulates the *Adafruit IO* REST and MQTT clients, as well as the *Arduino Cloud* client in wrapper classes. Most *f451 Labs* projects upload to and/or receive data from one or both of these services, and these wrappers simplifies these tasks by standardizing send and receive methods, and so on. The module also includes helper classes for handling cloud service feeds.
- **Colors** — includes RGB values for tons of colors
- **Common** — contains functions, variables, and constants that are common for most/all *f451 Labs* projects.
- **Logger** — encapsulates the default Python `Logging` class and adds a few more features that are commonly used in *f451 Labs* projects.

## Install

This module is not (yet) available on PyPi. However, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [tomli](https://pypi.org/project/tomli/) for Python < 3.11
- [tomllib](https://docs.python.org/3/library/tomllib.html) for Python >= 3.11

- [logging](https://docs.python.org/3/howto/logging.html)

- [adafruit-io](https://adafruit-io-python-client.readthedocs.io/en/latest/index.html)
- [arduino-iot-client](https://docs.arduino.cc/arduino-cloud/getting-started/arduino-iot-api#python)
- [requests-oauthlib](https://pypi.org/project/requests-oauthlib/)

- [pyfiglet](https://pypi.org/project/pyfiglet/) for creating fancy logos
- [rich](https://rich.readthedocs.io/en/stable/index.html)
- [sparklines](https://pypi.org/project/sparklines/)
- [termcolor](https://pypi.org/project/termcolor/) to color Sparkline graphs

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

```bash
$ pip install 'f451-common @ git+https://github.com/mlanser/f451-common.git'
```

## How to use

### Common module

Using the module is straightforward. Simply `import` the components of the module as needed in your code.

```Python
# Import specific components from the f451 Labs Common module
from f451_common.common import some_function, some_variable, some_constant

myVar = some_function()

# Import all components from the f451 Labs Common module
import f451_common.common as f451Common

myVar = f451Common.some_function()
```

#### Core classes & functions

- **init_cli_parser()** — Initialize the ArgParse parser with default CLI arguments.
- **is_valid()** — Verify that a given (sensor) value falls within a known valid absolute range.
- **is_in_range()** — Verify that a given (sensor) value falls within X% of a known valid range.
- **get_delta_range()** — Determine a given (sensor) value is above, below, or within a known range.
- **get_tri_colors()** — Get low-normal-high colors from a color map for a given sensor value.
- **load_settings()** — Initialize TOML parser and load settings file.
- **get_RPI_serial_num()** — Get Raspberry Pi serial number.
- **get_RPI_ID()** — Get Raspberry Pi ID. Also allows for additional pre- and/or suffix.
- **check_wifi()** — Check for Wi-Fi connection on Raspberry Pi.
- **num_to_range()** — Map numeric value to range.
- **convert_to_rgb()** — Map numeric value to RGB.
- **convert_to_bool()** — Convert value to boolean. Mainly used for config strings (e.g. "yes", "true", "on", etc.).
- **make_logo()** — Create fancy logo for CLI apps. This function uses the 'pyfiglet' library and the 'slant' font to create multi-line ASCII-art logos ... you're welcome! 🤓
- **Runtime** — Helper class for creating a global application runtime object.
- **FakeSensor** — Helper class for creating fake 'sensors' for testing, etc.

### Cloud module

To use this module you must have accounts with Adafruit IO and/or Arduino Cloud. This module creates
objects that make it easier to send data to and receive data from these services.

Simply `import` it the module into your code and instantiate the `AdafruitCloud` and/or `ArduinoCloud` object which you can then use throughout your code. You can also instantiate 'feed' objects for either service.

```Python
# Import f451 Labs Cloud
from f451_common.cloud import AdafruitCloud

# Initialize 'Cloud'
myPuffyCloud = AdafruitCloud(
    AIO_ID = "<ADAFRUIT IO USERNAME>", 
    AIO_KEY = "<ADAFRUIT IO KEY>"
)

# Create an Adafruit IO feed
feed = myPuffyCloud.create_feed('my-new-feed')

# Upload data to Adafruit IO feed
asyncio.run(myPuffyCloud.send_data(feed.key, randint(1, 100)))

# Receiving latest data from Adafruit IO feed
data = asyncio.run(myPuffyCloud.receive_data(feed.key, True))

# Adafruit IO returns data in form of 'namedtuple' and we can 
# use the '_asdict()' method to convert it to regular 'dict'.
# We then pass the 'dict' to 'json.dumps()' to prettify before 
# we print out the whole structure.
pretty = json.dumps(data._asdict(), indent=4, sort_keys=True)
print(pretty)
```

#### Core classes & functions

- **AdafruitCloud** — Main class for interacting with [Adafruit IO](https://io.adafruit.com) cloud service.
- **AdafruitFeed** — Helper class for managing Adafruit IO feeds.
- **AdafruitCloudError** — Helper class for managing IO errors related to Adafruit IO cloud service.

### Logger module

To use this module, you `import` it into your code and instantiate a `Logger` object which you can then use throughout your code.

```Python
# Import f451 Labs Logger
from f451_common.logger import Logger

# This is optional, but useful if you want to 
# use predefined constant for logging levels
import logging

# Instantiate using defaults ...
myLogger = Logger()

# ... or with custom log level and log file values
myLogger = Logger(
    logLvl=logging.ERROR, 
    logFile="path/to/mylogfile.log"
)

# Call 'log_xxxx' methods to log messages
myLogger.log_info("Hello world!")
myLogger.log_error("Oops! Something broke :-(")

# Call 'debug' method to show message in console
myLogger.debug("Hello world!")

myVar = 2
myLogger.debug(myVar)
```

#### Core classes & functions

- **Logger** — Main class for creating a `logger` object.

### CLI UI

This module is quite complex in that it can create fairly advanced UIs for *f451 Labs* projects with only a few lines of code. Of course, this requires some set-up and is not easily shown in a small expample.

In general, though, this module follows the same usage pattern as the other components of this module. Simply `import` the components of the module as needed, and call the functions from your code.

```Python
# Import specific components from the f451 Labs CLI UI module
from f451_common.cli_ui import some_function, some_variable, some_constant

myVar = some_function()

# Import all components from the f451 Labs CLI UI module
import f451_common.cli_ui as f451CLIUI

myVar = f451CLIUI.some_function()
```

Please refer to the `ui_demo` application for a more extensive example of how you can use the CLI UI library.

#### Core classes & functions

- **prep_data()** — Helper function to prep/format data for display via BasUI object.
- **BaseUI** — Helper class for creating a terminbal UI with a logo, 'actions' section, and data table.
- **Logo** — Helper class for creating fancy logos 🤓

### Colors

This module is very simple as its only purpose is to define a `dict` with a (long) list of color names and their corresponding RBG values as a `tuple` (e.g. `(0,0,0)` for black).

```Python
# Import COLORS
from f451_common.colors import COLORS

blackRBG = COLORS['black']
fancyBlueRBG = COLORS['cornflowerblue']
```

### UI Demo

The **f451 Labs Common** module includes a (fairly) comprehensive CLI UI demo which you can launch as follows:

```bash
$ python -m f451_common.ui_demo [<options>]

# If you have installed the 'f451 Labs Common' module 
# using the 'pip install'
$ ui_demo [<options>]

# Use CLI arg '-h' to see available options
$ ui_demo -h 
```

You can also also adjust the settings in the `ui_demo_settings.toml` file. For example, if you change the `WAIT` setting to some value greater than 1, then the UI will display a 'Waiting for sensor' progress bar. This allows us to handle scenarios where we need to wait between sensor read (e.g. waiting between running speed tests, etc.).

```toml
# File: ui_demo_settings.toml
...
WAIT = 10   # Wait 10 seconds until next sensor read
...
```

Finally you can exit the application using the `ctrl-c` command. If you use the `--uploads N` commandline argument, then the application will stop after *N* (simulated) uploads.

```bash
$ ui_demo --uploads 10
```

## How to test

The tests are written for [pytest](https://docs.pytest.org/en/7.1.x/contents.html) and we use markers to separate out tests that require the actual Sense HAT hardware. Some tests do not rely on the hardware to be present. However, those tests rely on the `pytest-mock` module to be present.

```bash

# Run all tests (except marked 'skip')
$ pytest

# Run tests with 'adafruit' marker
$ pytest -m "adafruit"

# Run tests without 'adafruit' marker
$ pytest -m "not adafruit"
```
