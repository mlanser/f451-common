# f451 Labs Common module v1.0.0

## Overview

The *f451 Labs Common* module contains functions, variables, and constants that are common for
most/all *f451 Labs* projects.

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [???](https://example.com)
- [???](https://example.com)

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
import f451_common

myVar = f451_common.common.some_function()
```
