"""Helper module for f451 Labs applications.

This module holds common helper functions and constants 
that can be used across most/all f451 Labs applications.

TODO:
 - add more/better tests
"""

import sys
import argparse
import random

from abc import ABC, abstractmethod
from datetime import datetime
from collections import namedtuple
from subprocess import check_output, STDOUT, DEVNULL
from pyfiglet import Figlet
from pathlib import Path

from .colors import COLORS as RGBColors

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__all__ = [  # noqa: F822
    'init_cli_parser',
    'is_valid',
    'is_in_range',
    'get_delta_range',
    'load_settings',
    'get_tri_colors',
    'get_RPI_serial_num',
    'get_RPI_ID',
    'check_wifi',
    'num_to_range',
    'convert_to_rgb',
    'convert_to_bool',
    'make_logo',
    'Runtime',
    'FakeSensor',
    'COLOR_MAP',
    'COLOR_LOW',
    'COLOR_NORM',
    'COLOR_HIGH',
    'DELIM_STD',
    'DELIM_VAL',
    'EMPTY_STR',
    'DEF_ID_PREFIX',
    'DEF_TEMP_COMP_FACTOR',
    'MAX_LEN_CPU_TEMPS',
    'STATUS_YES',
    'STATUS_ON',
    'STATUS_TRUE',
    'STATUS_NO',
    'STATUS_OFF',
    'STATUS_FALSE',
    'STATUS_UNKNOWN',
    'KWD_TEMP_COMP',
    'KWD_MAX_LEN_CPU_TEMPS',
]

# fmt: off
# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DELIM_STD = '|'
DELIM_VAL = ':'
EMPTY_STR = ''

DEF_ID_PREFIX = 'raspi-'  # Default prefix for ID string

# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
DEF_TEMP_COMP_FACTOR = 2.25
MAX_LEN_CPU_TEMPS = 5  # Max number of CPU temps

STATUS_YES = 'yes'
STATUS_ON = 'on'
STATUS_TRUE = 'true'

STATUS_NO = 'no'
STATUS_OFF = 'off'
STATUS_FALSE = 'false'

STATUS_UNKNOWN = 'unknown'

# =========================================================
#            C O L O R   M A P   C O N S T A N T S
# =========================================================
# This color map can be used for misc. sensor data. The goal 
# is to provide 5 colors that can indicate how a given value
# relates to the limits of a data set.
# 
# The set of limits for f451 Labs applications has 4 values.
# A limit set [A, B, C, D] means:
#
#             val <= A -> Dangerously Low   = "red"
#        B >= val >  A -> Low               = "yellow"
#        C >= val >  B -> Normal            = "green"
#        D >= val >  C -> High              = "cyan"
#             val >  D -> Dangerously High  = "blue"
#
COLOR_MAP = [
    'red',              # 0  -- These colors must also work
    'yellow',           # 1     with 'termcolor' library
    'green',            # 2
    'cyan',             # 3
    'blue',             # 4
]
# Shortcuts for indicating main colors
COLOR_LOW = 0
COLOR_NORM = 2
COLOR_HIGH = 4
# fmt: on


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_TEMP_COMP = 'TEMP_COMP'
KWD_MAX_LEN_CPU_TEMPS = 'CPU_TEMPS'


# =========================================================
#                 H E L P E R   C L A S S
# =========================================================
class Runtime(ABC):
    def __init__(
        self,
        appName,
        appVersion,
        appNameShort=None,
        appLog=None,
        appSettings=None,
        appHost=None,
        appDir=None,
    ):
        # Basic app info
        self.appName = appName
        self.appVersion = appVersion
        self.appNameShort = appNameShort
        self.appLog = appLog
        self.appSettings = appSettings
        self.appHost = appHost
        self.appDir = appDir

        # Core settings
        self.ioFreq = 0
        self.ioDelay = 0
        self.ioWait = 0
        self.ioThrottle = 0
        self.ioRounding = 0
        self.ioUploadAndExit = False

        # Core runtime variables
        self.workStart = datetime.now()
        self.timeSinceUpdate = float(0)
        self.timeUpdate = float(0)
        self.displayUpdate = float(0)
        self.uploadDelay = 0
        self.maxUploads = 0
        self.numUploads = 0

        # Core components
        self.config = None
        self.logger = None
        self.console = None

        # Placeholders for cloud service feeds,
        # connected sensors, and more
        self.feeds = {}
        self.sensors = {}

        # Debug and log levels
        self.logLvl = 0
        self.debugMode = False

    @abstractmethod
    def init_runtime(self, *args, **kwargs):
        pass

    @abstractmethod
    def show_summary(self, *args, **kwargs):
        pass

    @abstractmethod
    def debug(self, *args, **kwargs):
        pass


class FakeSensor:
    """Fake sensor class

    We use this class to simulate a sensor that generates some
    data. It's compatible with other sensor objects (e.g. SenseHat,
    Enviro, etc.). This makes it easier to add it as just another
    sensor object to the sensor list of an app object.
    """

    def __init__(self, *args, **kwargs):
        self._fake = None

    @staticmethod
    def get_demo_data(delta=None, default=None, outFmt='asNamed'):
        """Generate random data

        Args:
            delta: 'float' with ±% for range of values
            default: 'float' used for testing consistent values
            outFmt: 'str' defines output format
        Returns:
            'tuple', 'dict', or 'list'
        """

        # Set or generate first fake value
        if default is None:
            minVal = 1 if delta is None else max(1, int((1 - delta / 100) * 100))
            maxVal = 200 if delta is None else min(200, int((1 + delta / 100) * 100))
            rndNum = random.randint(minVal, maxVal)
        else:
            rndNum = default

        # Generate second value
        rndPcnt = random.randint(0, 100)

        if outFmt == 'asList':
            return [rndNum, rndPcnt]
        elif outFmt == 'asDict':
            return {'rndnum': rndNum, 'rndpcnt': rndPcnt}
        elif outFmt == 'asTuple':
            return (rndNum, rndPcnt)
        else:
            DataUnit = namedtuple('DataUnit', 'rndnum rndpcnt')
            return DataUnit(rndnum=rndNum, rndpcnt=rndPcnt)


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
def init_cli_parser(appName, appVersion, setDefaults=True):
    """Initialize CLI (ArgParse) parser.

    Initialize the ArgParse parser with default CLI 'arguments'
    and return new parser instance.

    Args:
        appName: 'str' with app name
        appVersion: 'str' with app version
        setDefaults: 'bool' flag indicates whether to set up default CLI args

    Returns:
        ArgParse parser instance
    """
    # fmt: off
    parser = argparse.ArgumentParser(
        prog=appName,
        description=f'{appName} [v{appVersion}] - collect internet speed test data using Speedtest CLI, and upload to Adafruit IO and/or Arduino Cloud.',
        epilog='NOTE: This application requires active accounts with corresponding cloud services.',
    )

    if setDefaults:
        parser.add_argument(
            '-V',
            '--version',
            action='store_true',
            help='display script version number and exit',
        )
        parser.add_argument(
            '-d', 
            '--debug', 
            action='store_true', 
            default=False,
            help='run script in debug mode'
        )
        parser.add_argument(
            '--log',
            action='store',
            type=str,
            help='name of log file',
        )

    return parser
    # fmt: off


def get_tri_colors(colors=None, asRGB=False):
    """Get low-normal-high colors

    We used this set of colors to color-code values based on
    how they relate to data limits for a given data set.

    NOTE: This function can return color values as strings (used
          for creating ANSI color codes), or as RGB values (as
          tuples) which are by Sense HAT library (and others)
          to color a graph value, etc.

    Args:
        colors: optional set of custom colors
        asRGB: returns RGB values instead of color names as strings

    Returns:
        TriColor (named tuple) with color names as strings or RGB values (as tuples)
    """
    TriColor = namedtuple('TriColor', 'low normal high')

    colorMap = COLOR_MAP if colors is None else colors

    if asRGB:
        return TriColor(
            RGBColors[colorMap[COLOR_LOW]],  # e.g. (255, 0, 0)
            RGBColors[colorMap[COLOR_NORM]],
            RGBColors[colorMap[COLOR_HIGH]],
        )
    else:
        return TriColor(
            colorMap[COLOR_LOW],  # e.g. 'red'
            colorMap[COLOR_NORM],
            colorMap[COLOR_HIGH],
        )


def is_valid(val, valid, allowNone=True):
    """Verify value 'valid'

    We know what 'valid' ranges are for each sensor.
    This method allows us to verify that a given
    value falls within that range. Any value outside
    the range should be considered an error.

    NOTE: If 'valid' is 'None' or '(None, None)', then we
          assume that any value is valid. However, if
          one or both items in the 'valid' tuple are not
          'None', then we'll compare aaginst that item.

    Args:
        val: value to check
        valid: 'tuple' with min/max values for valid range
        allowNone: if 'True', then skip compare if 'valid' is 'None

    Returns:
        'True' if value is valid, else 'False'
    """
    if valid is None or not all(valid):
        return allowNone

    if val is not None and any(valid):
        isValid = True
        if valid[0] is not None:
            isValid &= float(val) >= float(valid[0])
        if valid[1] is not None:
            isValid &= float(val) <= float(valid[1])

        return isValid

    return False


def is_in_range(first, second, factor):
    """Check if 1st value is within X% of 2nd value

    This method allows us to check if a value falls
    within a given range.

    Args:
        first: value to compare
        second: value to compare against
        factor: factor to extend range for comparison

    Returns:
        'True' if value is in range, else 'False'
    """
    # If either value is 'None' then we'll assume that
    # there is 'no change' ... 'coz we can't compare
    if first is None or second is None:
        return True

    lower = second * (1 - factor)
    upper = second * (1 + factor)

    return is_valid(first, (lower, upper))


def get_delta_range(first, second, factor):
    """Check if 1st value is within X% of 2nd value

    This method allows us to compare 2 values to see
    if they're equal-ish, and we can use this to even
    out minor deviations between sensor readings.

    Args:
        first: value to compare
        second: value to compare against
        factor: factor to extend range for comparison

    Returns:
        1: above range
        0: within range
        -1: below range
    """
    # If either value is 'None' then we have to
    # assume 'no change' ... 'coz we can't compare
    if first is None or second is None:
        return 0

    # fmt: off
    lower = second * (1 - factor)
    upper = second * (1 + factor)
    if float(first) > upper:    # Above range
        return 1
    elif float(first) < lower:  # Below range
        return -1
    else:
        return 0                # Within range
    # fmt: on


def load_settings(settingsFile):
    """Initialize TOML parser and load settings file

    Args:
        settingsFile: path object or string with filename

    Returns:
        'dict' with values from TOML file
    """
    try:
        with open(settingsFile, mode='rb') as fp:
            settings = tomllib.load(fp)

    except (FileNotFoundError, tomllib.TOMLDecodeError):
        sys.exit(f"Missing or invalid file: '{settingsFile}'")

    else:
        return settings


def get_RPI_serial_num():
    """Get Raspberry Pi serial number

    Based on code from Enviro+ example 'luftdaten_combined.py'

    Returns:
        'str' with RPI serial number or 'None' if we can't find it
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[:6] == 'Serial':
                    return line.split(':')[1].strip()
    except OSError:
        return None


def get_RPI_ID(prefix='', suffix='', default='n/a'):
    """Get Raspberry Pi ID

    Returns a string with RPI ID (i.e. serial num with pre- and suffix).

    Args:
        prefix: optional prefix
        suffix: optional suffix
        default: optional default string to be returned if no serial num

    Returns:
        'str' with RPI ID
    """
    serialNum = get_RPI_serial_num()

    return f'{prefix}{serialNum}{suffix}' if serialNum else default


def check_wifi():
    """Check for Wi-Fi connection on Raspberry Pi

    Based on code from Enviro+ example 'luftdaten_combined.py'

    TODO: find better way to do this

    Returns:
        'True' - wi-fi confirmed
        'False' - status unknown
    """
    try:
        result = check_output(['hostname', '-I'], stderr=DEVNULL)
    except Exception:
        result = None

    return result is not None


def num_to_range(num, inMinMax, outMinMax, force=False):
    """Map numeric value to range

    We use this function to map values (e.g. temp, etc.) against the a limited range
    of values.

    For example, the Y-axis of the SenseHat 8x8 LED display has only 8 LEDs,
    which means that all values must be mapped against a range of 0-8 where we use
    0 for "off" and 1-8 to light up the corresponding LED.

    Another example is the 'Sparklines' library which uses 8 different characters to
    create sparkline graphs in the terminal. Here too we map against a range of 0-8.

    Based on code found here: https://www.30secondsofcode.org/python/s/num-to-range/

    Args:
        num:
            Number to map against range
        inMinMax:
            'tuple' with min/max values of range for numbers to be converted
        outMinMax:
            'tuple' with min/max value of target range
        force:
            'bool' if 'True' then any 'num' outside 'inMinMax' and any 'None" value will
            be adjusted to stay in range. If too small (or 'None'), then it'll be set to
            min, and if too large, it'll be set to max.

            If 'False', then any 'None' will remain 'None' and any out-of-bound value
            will be set to 'None' as well.
    Returns:
        'float' if valid or 'None' if missing/invalid
    """
    if inMinMax[0] > inMinMax[1]:
        raise ValueError(f"Invalid 'inMinMax' values: ({inMinMax[0]},{inMinMax[1]})")

    if outMinMax[0] > outMinMax[1]:
        raise ValueError(f"Invalid 'outMinMax' values: ({outMinMax[0]},{outMinMax[1]})")

    deltaInMinMax = (inMinMax[1] - inMinMax[0]) if inMinMax[1] != inMinMax[0] else 1
    deltaOutMinMax = (outMinMax[1] - outMinMax[0]) if outMinMax[1] != outMinMax[0] else 1

    if num is None:
        num = inMinMax[0] if force else None

    elif num < inMinMax[0] or num > inMinMax[1]:
        num = min(max(num, inMinMax[0]), inMinMax[1]) if force else None

    if num is None:
        return None

    val = outMinMax[0] + (float(num - inMinMax[0]) / float(deltaInMinMax) * float(deltaOutMinMax))
    return float(max(min(val, outMinMax[1]), outMinMax[0]))


def convert_to_rgb(num, inMin, inMax, colors):
    """Map numeric value to RGB

    Based on reply found on StackOverflow by `martineau`:

    See: https://stackoverflow.com/questions/20792445/calculate-rgb-value-for-a-range-of-values-to-create-heat-map

    Args:
        num:
            Number to convert/map to RGB
        inMin:
            Min value of range for numbers to be converted
        inMax:
            Max value of range for numbers to be converted
        colors:
            series of RGB colors delineating a series of adjacent
            linear color gradients.

    Returns:
        'tuple' with RGB value
    """
    EPSILON = sys.float_info.epsilon  # Smallest possible difference

    # Determine where the given value falls proportionality within
    # the range from inMin->inMax and scale that fractional value
    # by the total number in the `colors` palette.
    i_f = float(num - inMin) / float(inMax - inMin) * (len(colors) - 1)

    # Determine the lower index of the pair of color indices this
    # value corresponds and its fractional distance between the lower
    # and the upper colors.
    i, f = int(i_f // 1), i_f % 1  # Split into whole & fractional parts.

    # Does it fall exactly on one of the color points?
    if f < EPSILON:
        return colors[i]

    # ... if not, then return a color linearly interpolated in the
    # range between it and the following one.
    (r1, g1, b1), (r2, g2, b2) = colors[i], colors[i + 1]
    return int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1))


def convert_to_bool(inVal):
    """Convert value to boolean.

    If value is a string, then we check against predefined string
    constants. If value is an integer, then we return 'True' if value
    is greater than 0 (zero).

    For anything else we return a 'False'.

    Args:
        inVal:
            Value to be converted to boolean.
    """
    if isinstance(inVal, bool):
        return inVal
    elif isinstance(inVal, (int, float)):
        return abs(int(inVal)) > 0
    elif isinstance(inVal, str):
        return inVal.lower() in [STATUS_ON, STATUS_TRUE, STATUS_YES]
    else:
        return False


def make_logo(maxWidth, appName, appVer, default=None, center=True):
    """Create a fancy logo using pyFiglet

    This will create a fancy multi-line ASCII-ized logo
    using pyFiglet library and 'slant' font. We'll also
    add in the version number on the last row, and we'll
    center the logo if theres enough space.

    If there is not enough space for  abig logo, then we
    can return a default string instead.

    Args:
        maxWidth:
            'int' max length of any row in the logo (usually console width)
        appName:
            'str' application name to use for logo
        appVer:
            'str' application version number. We'll prefix it with a 'v'
        default:
            'str' default string if space is too tight
        center:
            'bool' if True, then we'll 'center' logo lines within available space

    Returns:
        'str' with logo. A multiline-logo will have '\n' embedded
    """
    logoFont = Figlet(font='slant')
    logoStrArr = logoFont.renderText(appName).splitlines()
    logoLen = max(len(s) for s in logoStrArr)

    result = default

    if logoLen < maxWidth:
        lastCharPos = logoStrArr[-2].rfind('/')
        deltaStrLen = (
            len(logoStrArr[-2]) - lastCharPos
            if lastCharPos >= 0
            else len(logoStrArr[-2]) - len(appVer)
        )
        logoStrArr[-1] = (
            logoStrArr[-1][: -(len(appVer) + deltaStrLen)] + appVer + (' ' * deltaStrLen)
        )
        newLogo = [s.center(maxWidth, ' ').rstrip() for s in logoStrArr] if center else logoStrArr
        result = '\n'.join(newLogo)

    return result


# =========================================================
#                    M O D U L E   D E M O
# =========================================================
def main():
    APP_DIR = Path(__file__).parent  # Find dir for this app
    settingsFile = 'demo.toml'
    settings = load_settings(APP_DIR.joinpath(settingsFile))

    print('\n====== [Demo of f451 Labs Common module] ======\n')

    print(make_logo(40, 'Test', 'v0.0.0', 'Test (v0.0.0)'))

    print('\n-----------------------------------------------\n')

    print(f"Reading values from '{settingsFile}' file:\n")
    for k, v in settings.items():
        print(f'  {k} = {v}')

    print('\n=============== [End of Demo] =================\n')


if __name__ == '__main__':
    main()
