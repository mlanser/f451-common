# f451 Labs Common module v1.1.0

## Overview

The *f451 Labs Common* module contains functions, variables, and constants that are common for
most/all *f451 Labs* projects.

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [pyfiglet](https://pypi.org/project/pyfiglet/)
- [tomli](https://pypi.org/project/tomli/) for Python < 3.11
- [tomllib](https://docs.python.org/3/library/tomllib.html) for Python >= 3.11

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

Using HTTPS:

```bash
$ pip install 'f451-common @ git+https://github.com/mlanser/f451-common.git'
```

Using SSH:

```bash
$ pip install 'f451-common @ git+ssh://git@github.com:mlanser/f451-common.git'
```

## How to use

Using the module is straightforward. Simply `import` the components of the module as needed in your code.

```Python
# Import specific components from f451 Labs Common module
from f451_common.common import some_function, some_variable, some_constant

myVar = some_function()

# Import all components f451 Labs Common module
import f451_common.common as f451Common

myVar = f451Common.some_function()
```

## Core functions

- **load_settings()** — Initialize TOML parser and load settings file.
- **get_RPI_serial_num()** — Get Raspberry Pi serial number.
- **get_RPI_ID()** — Get Raspberry Pi ID. Also allows for additional pre- and/or suffix.
- **check_wifi()** — Check for Wi-Fi connection on Raspberry Pi.
- **num_to_range()** — Map numeric value to range.
- **convert_to_rgb()** — Map numeric value to RGB.
- **convert_to_bool()** — Convert value to boolean. Mainly used for config strings (e.g. "yes", "true", "on", etc.)
- **make_logo()** — Create fancy logo for CLI apps. This function uses the 'pyfiglet' library and the 'slant' font to create multi-line ASCII-art logos ... you're welcome! 🤓
