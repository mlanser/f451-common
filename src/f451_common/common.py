"""Helper module for f451 Labs applications.

This module holds common helper functions and constants 
that can be used across most/all f451 Labs applications.
"""

import sys
from subprocess import check_output, STDOUT, DEVNULL  # noqa: F401
from pyfiglet import Figlet

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__all__ = [  # noqa: F822
    'load_settings',
    'get_RPI_serial_num',
    'get_RPI_ID',
    'check_wifi',
    'num_to_range',
    'convert_to_rgb',
    'convert_to_bool',
    'make_logo',
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
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_TEMP_COMP = 'TEMP_COMP'
KWD_MAX_LEN_CPU_TEMPS = 'CPU_TEMPS'


# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
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
                if line[0:6] == 'Serial':
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

    return f"{prefix}{serialNum}{suffix}" if serialNum else default


def check_wifi():
    """Check for Wi-Fi connection on Raspberry Pi

    Based on code from Enviro+ example 'luftdaten_combined.py'

    TODO: verify better way to do this

    Returns:
        'True' - wi-fi confirmed
        'False' - status unknown
    """
    try:
        result = check_output(['hostname', '-I'], stderr=DEVNULL)
    except Exception:
        result = None

    return True if result is not None else False


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
    else:
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
    elif isinstance(inVal, int) or isinstance(inVal, float):
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
    logoLen = max([len(s) for s in logoStrArr])

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
