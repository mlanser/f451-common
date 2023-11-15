# f451 Labs Logger module v1.0.0

## Overview

The *f451 Labs Logger* module encapsulates the default Python `Logging` class and adds a few more features that are commonly used in *f451 Labs* projects.

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [logging](https://docs.python.org/3/howto/logging.html)
- [pprint](https://docs.python.org/3/library/pprint.html)

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

Using HTTPS:

```bash
$ pip install 'f451-logger @ git+https://github.com/mlanser/f451-logger.git'
```

Using SSH:

```bash
$ pip install 'f451-logger @ git+ssh://git@github.com:mlanser/f451-logger.git'
```

## How to use

Using the module is straightforward. Simply `import` it into your code and instantiate a `Logger` object which you can then use throughout your code.

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
