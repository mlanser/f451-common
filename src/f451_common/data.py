"""f451 Labs Common Data module.

The f451 Labs Data module encapsulates gSpread and other libraries to standardize
processes for reading from and writing data to various (simple) data storage mechanisms
specifically for f451 Labs Projects applications.

However, the purpose is not to replace proper ORMs or even to replicate all functions 
from gSpread. Instead, this module simply wraps a few common processes with the same
API so that applications can easily switch between storage mechanisms without requiring
any major changes to the code.

TODO:
 - update module demo
 - add Arduino Cloud code
 - more tests

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

import gspread

__all__ = [
    'GoogleSheet',
    'KWD_GOOGLE_SA',
    'KWD_SPREADSHEET',
    'KWD_WORKSHEET',
]


# Install Rich 'traceback' and 'pprint' to
# make (debug) life is easier. Trust me!
from rich.pretty import pprint
from rich.traceback import install as install_rich_traceback

install_rich_traceback(show_locals=True)


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
# fmt: off
KWD_GOOGLE_SA = 'GOOGLE_SA'         # Google API Service Account Info
KWD_SPREADSHEET = 'SPREADSHEET'     # Spreadsheet name
KWD_WORKSHEET = 'WORKSHEET'         # Worksheet/tab name
# fmt: on


# =========================================================
#                        H E L P E R S
# =========================================================
class Spreadsheet(ABC):
    """Basic spreadsheet class.

    This class is the base for all spreadsheet classes. It holds
    some common methods and properties to ensure a basic level of
    compatibility between the spreadsheet objects.
    """

    def __init__(self, spreadsheet, defWrkSht=None, active=False):
        self._spreadsheet = spreadsheet
        self._defWrkSht = defWrkSht
        self._active = active

    @property
    def is_active(self):
        return self._active

    @property
    def spreadsheet(self):
        return self._spreadsheet

    @abstractmethod
    def read_data_from_cell(self, cell, worksheet):
        pass

    @abstractmethod
    def read_data_from_range(self, cellRange, worksheet):
        pass

    @abstractmethod
    def write_data_to_cell(self, cell, worksheet):
        pass

    @abstractmethod
    def write_data_to_range(self, cellRange, worksheet):
        pass


# =========================================================
#                   M A I N   C L A S S E S
# =========================================================
class GoogleSheet(Spreadsheet):
    """Main class for managing Google Sheet API.

    This class encapsulates the gSpread library and helps us standardize 
    spreadsheet read and write functions across different types of 
    spreadsheets (e.g. Google Sheets, Excel, CDSV, etc.).

    NOTE: attributes follow same naming convention as used
    in the 'settings.toml' file. This makes it possible to pass
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myGS = GoogleSheet(config)           # Use values from 'config'
        myGS = GoogleSheet(key=val)          # Use val
        myGS = GoogleSheet(config, key=val)  # Use values from 'config' and also use 'val'

    Attributes:
        GOOGLE_SA:              Google API Service Account Info
        SPREADSHEET:            Spreadsheet name
        WORKSHEET:              Worksheet/tab name

    Methods:
        read_data_from_cell:    Read value from single spreadsheet cell
        read_data_from_range:   Read values from range of spreadsheet cells
        write_data_to_cell:     Write value to single spreadsheet cell
        write_data_to_range:    Write values to range of spreadsheet cells
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
        gcSA = None
        sht = None
        defWrkSht = None

        try:
            gcSAFile = settings.get(KWD_GOOGLE_SA)
            shtName = settings.get(KWD_SPREADSHEET)
            defWrkSht = settings.get(KWD_WORKSHEET)
            gcSA = gspread.service_account(filename=gcSAFile)
            sht = gcSA.open(shtName)
            active = True

        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"ERROR: Unable to open Google Sheet - {e}")
            sys.exit(1)

        if gcSA and sht:
            super().__init__(sht, defWrkSht, active)

    def read_data_from_cell(self, cell, wrkSheet=None):
        wrkSheet = self._defWrkSht if wrkSheet is None else wrkSheet

        objWrkSheet = None
        if isinstance(wrkSheet, int):
            objWrkSheet = self._spreadsheet.get_worksheet(wrkSheet)
        elif isinstance(wrkSheet, str):
            objWrkSheet = self._spreadsheet.worksheet(wrkSheet)

        return objWrkSheet.acell(cell).value if objWrkSheet is not None else None

    def read_data_from_range(self, cellRange, wrkSheet=None):
        wrkSheet = self._defWrkSht if wrkSheet is None else wrkSheet

        objWrkSheet = None
        if isinstance(wrkSheet, int):
            objWrkSheet = self._spreadsheet.get_worksheet(wrkSheet)
        elif isinstance(wrkSheet, str):
            objWrkSheet = self._spreadsheet.worksheet(wrkSheet)

        return objWrkSheet.get_values(cellRange)

    def write_data_to_cell(self, cell, worksheet):
        pass

    def write_data_to_range(self, cellRange, worksheet):
        pass



# =========================================================
#                    M O D U L E   D E M O
# =========================================================
if __name__ == '__main__':
    # Initialize TOML parser and try to load 'settings.toml' file
    currDir = Path(__file__).parent
    try:
        with open(currDir.joinpath('settings.toml'), mode='rb') as fp:
            config = tomllib.load(fp)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        # fmt: off
        config = {
            'GOOGLE_SA': None,      # Set your 'Google API Service Account'
            'SPREADSHEET': None,    # Define spreadsheet name
            'WORKSHEET': None,      # Define default worksheet name
        }
        # fmt: on

    # Check for creds
    if not config.get('GOOGLE_SA') or not config.get('SPREADSHEET'):
        sys.exit('ERROR: Missing Google Sheet credentials')

    saFN = config.get('GOOGLE_SA')
    config['GOOGLE_SA'] = currDir.joinpath(saFN)
    pprint(config)

    testSheet = GoogleSheet(config)
    print('\n===== [Demo of f451 Labs Data Module] =====')
    print(testSheet.read_data_from_cell('A2'))
    print(testSheet.read_data_from_cell('B3'))
    print(testSheet.read_data_from_range('TestRange'))
    print('\n--------------------------------------------')
    print('=============== [End of Demo] =================\n')
