# f451 Labs Common module v2.1.0

## Overview

This module consists of the following cor components:

- **Common** — contains functions, variables, and constants that are common for most/all *f451 Labs* projects.
- **Cloud** — encapsulates the *Adafruit IO* REST and MQTT clients, as well as the *Arduino Cloud* client in wrapper classes. Most *f451 Labs* projects upload to and/or receive data from one or both of these services, and these wrappers simplifies these tasks by standardizing send and receive methods, and so on. The module also includes helper classes for handling cloud service feeds.
- **Logger** — encapsulates the default Python `Logging` class and adds a few more features that are commonly used in *f451 Labs* projects.
- **CLI UI** — contains functions, variables, and constants that can be used to create common UI elements for *f451 Labs* projects.

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

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

#### Core functions

- **load_settings()** — Initialize TOML parser and load settings file.
- **get_RPI_serial_num()** — Get Raspberry Pi serial number.
- **get_RPI_ID()** — Get Raspberry Pi ID. Also allows for additional pre- and/or suffix.
- **check_wifi()** — Check for Wi-Fi connection on Raspberry Pi.
- **num_to_range()** — Map numeric value to range.
- **convert_to_rgb()** — Map numeric value to RGB.
- **convert_to_bool()** — Convert value to boolean. Mainly used for config strings (e.g. "yes", "true", "on", etc.)
- **make_logo()** — Create fancy logo for CLI apps. This function uses the 'pyfiglet' library and the 'slant' font to create multi-line ASCII-art logos ... you're welcome! 🤓

### Cloud module

To use thios module you must have accounts with Adafruit IO and/or Aduino Cloud. This module creates
objects that make it easier to send data to and receive data from these services.

Simply `import` it the module into your code and instantiate the `AdafruitCloud` and/or `ArduinoCloud` object which you can then use throughout your code. You can also instantiate 'feed' objects for either service.

```Python
# Import f451 Labs Cloud
from f451_cloud.cloud import Cloud

# Initialize 'Cloud'
myCloud = Cloud(
    AIO_ID = "<ADAFRUIT IO USERNAME>", 
    AIO_KEY = "<ADAFRUIT IO KEY>"
)

# Create an Adafruit IO feed
feed = myCloud.aio_create_feed('my-new-feed')

# Upload data to Adafruit IO feed
asyncio.run(myCloud.aio_send_data(feed.key, randint(1, 100)))

# Receiving latest data from Adafruit IO feed
data = asyncio.run(myCloud.aio_receive_data(feed.key, True))

# Adafruit IO returns data in form of 'namedtuple' and we can 
# use the '_asdict()' method to convert it to regular 'dict'.
# We then pass the 'dict' to 'json.dumps()' to prettify before 
# we print out the whole structure.
pretty = json.dumps(data._asdict(), indent=4, sort_keys=True)
print(pretty)
```

### Logger module

To use this module, you `import` it into your code and instantiate a `Logger` object which you can then use throughout your code.

```Python
# Import f451 Labs Logger
from f451_logger.logger import Logger

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

### CLI UI

This module is quite complex in that it can create fairly advanced UIs for *f451 Labs* projects with only a few lines of code. Of course, this requires some set-up and is not easily shown in a small expample.

In general, though, this module follows the same usage pattern as the other components of this module. Simply `import` the components of the module as needed, and call the functions from your code.

```Python
# Import specific components from the f451 Labs CLI UI module
from f451_cli_ui.cli_ui import some_function, some_variable, some_constant

myVar = some_function()

# Import all components from the f451 Labs CLI UI module
import f451_cli_ui.cli_ui as f451CLIUI

myVar = f451CLIUI.some_function()
```

Please refer to the `ui_demo` application for a more extensive example of how you can use the the CLI UI library.

If you have install the **f451 Labs Common** module using the `pip install` command, then you

You can launch the CLI UI demo as follows:

```bash
$ python -m f451_common.ui_demo [<options>]

# If you have installed the 'f451 Labs Common' module 
# using the 'pip install'
$ ui_demo [<options>]

# Use CLI arg '-h' to see available options
$ ui_demo -h 
```

You can also also adjust the settings in the `ui_demo_settings.toml` file. For example, if you change the `WAIT` setting to some value greater that 1, then the UI will display a 'Waiting for sensor' progress bar. This allows us to handle scenarios where we need to wait between sensor read (e.g. waiting between running speed tests, etc.).

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
