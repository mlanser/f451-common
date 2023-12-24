"""f451 Labs Common CLI UI module.

This class defines and manages the layout and display of 
data in the terminal. This is, however, not a complete TUI
as most f451 Labs applications only collect and display data.

We're using a few libraries to make this all look pretty:

TODO:
    - create more/better tests
    - create demo for module

Dependencies:
    - rich - handles UI layout, etc.
    - sparklines - display real-time-ish data as sparklines
    - termcolor - adds colors to sparklines 
"""

import time

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.rule import Rule
from rich.status import Status
from rich.table import Table

from sparklines import sparklines

import f451_common.common as f451Common


__all__ = [
    'BaseUI',
    'Logo',
    'prep_data',
]


# fmt: off
# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
APP_1COL_MIN_WIDTH = 40     # Min width (in chars) for 1col terminal layout
APP_2COL_MIN_WIDTH = 80     # Min width (in chars) for 2col terminal layout
APP_MIN_CLI_HEIGHT = 10     # Min terminal window height (in rows)

APP_DELTA_FACTOR = 0.02     # Any change within X% is considered negligable

STATUS_OK = 200

STATUS_LBL_NEXT = 'Next:  '
STATUS_LBL_LAST = 'Last:  '
STATUS_LBL_TOT_UPLD = 'Total: '
STATUS_LBL_WAIT = 'Waiting …'
STATUS_LBL_INIT = 'Initializing …'
STATUS_LBL_UPLD = 'Uploading …'

HDR_STATUS = 'Uploads'
VAL_BLANK_STR = '--'        # Use for 'blank' data
VAL_ERROR_STR = 'Error'     # Use for invalid data

COLOR_DEF = 'grey'          # Default color
COLOR_OK = 'green'
COLOR_ERROR = 'red'

CHAR_DIR_UP = '↑'           # UP arrow to indicate increase
CHAR_DIR_EQ = '↔︎'           # SIDEWAYS arrow to little/no change
CHAR_DIR_DWN = '↓'          # DOWN arrow to indicate decline
CHAR_DIR_DEF = ' '          # 'blank' to indicate unknown change

MAX_PROGBAR = 100           # Use 100% as max for progress bars
# fmt: o2


# =========================================================
#    H E L P E R   C L A S S E S   &   F U N C T I O N S
# =========================================================
class Logo:
    """Render fancy logo."""

    def __init__(self, width, namePlain, nameRender, verNum):
        self._render = f451Common.make_logo(width, nameRender, f"v{verNum}")
        self._plain = f"{namePlain} - v{verNum}"

    @property
    def rows(self):
        return max(self._render.count('\n'), 1) if self._render else 1

    @property
    def plain(self):
        return self._plain

    def __rich__(self):
        return Text(str(self._render), end='')

    def __str__(self):
        return self._plain

    def __repr__(self):
        return f"{type(self).__name__}(plain={self._plain!r})"


def prep_data(inData, dataTypes, deltaFactor=APP_DELTA_FACTOR, labelsOnly=False, conWidth=APP_2COL_MIN_WIDTH):
    """Prep data for display in terminal

    We display a table in the terminal with a row for each data type. On
    each row, we the display label, last value (with unit), and a sparkline
    graph.

    This function will filter data to ensure we don't have incorrect
    outliers (e.g. from faulty sensors, etc.). The final data set will
    have only valid values. Any invalid values will be replaced with
    0's so that we can display the set as a sparkline graph.

    This will technically affect the min/max values for the set. However,
    we're displaying this data in a table cells that will have about
    40 columns, and each column is made up of block characters which
    can only show 8 different heights. So visual 'accuracy' is
    already less than ideal ;-)

    NOTE: We need to map the data sets agains a numeric range of 1-8 so
          that we can display them as sparkline graphs in the terminal.

    NOTE: We're using the 'limits' list to color the values, which means
          we need to create a special 'coloring' set for the sparkline
          graphs using converted limit values.

          The limits list has 4 values (see also 'SenseData' class) and
          we need to map them to colors:

          Limit set [A, B, C, D] means:

                     val <= A -> Dangerously Low    = "bright_red"
                B >= val >  A -> Low                = "bright_yellow"
                C >= val >  B -> Normal             = "green"
                D >= val >  C -> High               = "cyan"
                     val >  D -> Dangerously High   = "blue"

          Note that the Sparkline library has a specific syntax for
          limits and colors:

            "<name of color>:<gt|eq|lt>:<value>"

          Also, we only care about 'low', 'normal', and 'high'

    Args:
        inData: 'dict' with Sense HAT data
        dataTypes: 'list' of data type names (e.g. 'temperature, 'humidity', etc.)
        labelsOnly: 'bool' if True then only display data labels
        conWidth: 'int' console width used for determining size of table, etc.
        deltaFactor: 'float' Any change within X% is considered negligable

    Returns:
        'list' with processed data and only with data rows (i.e. temp,
        humidity, pressure) and columns (i.e. label, last data pt, and
        sparkline) that we want to display. Each row in the list is
        designed for display in the terminal.
    """
    outData = []

    def _sparkline_colors(limits, customColors=None):
        """Create color mapping for sparkline graphs

        This function creates the 'color' list which allows
        the 'sparklines' library to add add correct ANSI
        color codes to the graph.

        Args:
            limits: list with limits -- see SenseHat module for details
            customColors: (optional) custom color map

        Return:
            'list' with definitions for 'emph' param of 'sparklines' method
        """
        # fmt: off
        colors = None

        if all(limits):
            colorMap = f451Common.get_tri_colors(customColors)

            colors = [
                f'{colorMap.high}:gt:{round(limits[2], 1)}',    # High   # type: ignore
                f'{colorMap.normal}:eq:{round(limits[2], 1)}',  # Normal # type: ignore
                f'{colorMap.normal}:lt:{round(limits[2], 1)}',  # Normal # type: ignore
                f'{colorMap.low}:eq:{round(limits[1], 1)}',     # Low    # type: ignore
                f'{colorMap.low}:lt:{round(limits[1], 1)}',     # Low    # type: ignore
            ]

        return colors
        # fmt: on

    def _dataPt_color(val, limits, default='', customColors=None):
        """Determine color mapping for specific value

        Args:
            val: value to check
            limits: list with limits -- see SenseHat module for details
            default: (optional) default color name string
            customColors: (optional) custom color map

        Return:
            'list' with definitions for 'emph' param of 'sparklines' method
        """
        color = default
        colorMap = f451Common.get_tri_colors(customColors)

        if val is not None and all(limits):
            if val > round(limits[2], 1):
                color = colorMap.high
            elif val <= round(limits[1], 1):
                color = colorMap.low
            else:
                color = colorMap.normal

        return color

    # Process each data row and create a new data structure that we can use
    # for displaying all necessary data in the terminal.
    for key, row in inData.items():
        if key in dataTypes:
            # Create new crispy clean set :-)
            dataSet = {
                'sparkData': [],
                'sparkColors': None,
                'sparkMinMax': (None, None),
                'dataPt': None,
                'dataPtOK': True,
                'dataPtDelta': 0,
                'dataPtColor': '',
                'unit': row['unit'],
                'label': row['label'],
            }

            # If we only need labels, then we'll skip to
            # next iteration of the loop
            if labelsOnly:
                outData.append(dataSet)
                continue

            # Data slice we can display in table row
            graphWidth = min(int(conWidth / 2), 40)
            dataSlice = list(row['data'])[-graphWidth:]

            # Get filtered data to calculate min/max. Note that 'valid' data
            # will have only valid values. Any invalid values would have been
            # replaced with 'None' values. We can display this set using the
            # 'sparklines' library. We continue refining the data by removing
            # all 'None' values to get a 'clean' set, which we can use to
            # establish min/max values for the set.
            dataValid = [i if f451Common.is_valid(i, row['valid']) else None for i in dataSlice]
            dataClean = [i for i in dataValid if i is not None]

            # We set 'OK' flag to 'True' if current data point is valid or
            # missing (i.e. None).
            dataPt = dataSlice[-1] if f451Common.is_valid(dataSlice[-1], row['valid']) else None
            dataPtOK = dataPt or dataSlice[-1] is None

            # We determine up/down/sideways trend by looking at delate between
            # current value and previous value. If current and/or previous value
            # is 'None' for whatever reason, then we assume 'sideways' (0)trend.
            dataPtPrev = (
                dataSlice[-2] if f451Common.is_valid(dataSlice[-2], row['valid']) else None
            )
            dataPtDelta = f451Common.get_delta_range(dataPt, dataPtPrev, deltaFactor)

            # Update data set
            dataSet['sparkData'] = [0 if i is None else i for i in dataValid]
            dataSet['sparkColors'] = _sparkline_colors(row['limits'])
            dataSet['sparkMinMax'] = (
                (min(dataClean), max(dataClean)) if any(dataClean) else (None, None)
            )

            dataSet['dataPt'] = dataPt
            dataSet['dataPtOK'] = dataPtOK
            dataSet['dataPtDelta'] = dataPtDelta
            dataSet['dataPtColor'] = _dataPt_color(dataPt, row['limits'])

            outData.append(dataSet)

    return outData


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class BaseUI:
    def __init__(self):
        self._console = Console()
        self._layout = Layout()
        self._conWidth = 0
        self._conHeight = 0
        self._active = False
        self._progBar = None
        self._progTaskID = None
        self.logo = None
        self.show24h = False    # Show 24-hour time?
        self.showLocal = True   # Show local time?
        self.statusHdr = HDR_STATUS
        self.statusLblNext = STATUS_LBL_NEXT
        self.statusLblLast = STATUS_LBL_LAST
        self.statusLblTotUpld = STATUS_LBL_TOT_UPLD

    @property
    def is_dual_col(self):
        return self._conWidth >= APP_2COL_MIN_WIDTH

    @property
    def conWidth(self):
        return self._conWidth
    
    @property
    def is_active(self):
        return self._active

    @property
    def console(self):
        """Provide hook to Rich 'console'"""
        return self._console if self._active else None

    @property
    def layout(self):
        """Provide hook to Rich 'layout'"""
        return self._layout if self._active else None

    @property
    def statusbar(self):
         """Provide hook to Rich 'status'"""
         return self._layout['actCurrent'] if self._active else None

    def _make_time_str(self, t):
        timeFmtStr = '%H:%M:%S' if self.show24h else '%I:%M:%S %p'
        return time.strftime(timeFmtStr, time.localtime(t) if self.showLocal else time.gmtime(t))

    @staticmethod
    def _make_footer(appName, width, customColors=None):
        """Create 'footer' object"""
        colorMap = f451Common.get_tri_colors(customColors)
        footer = Text()

        # Assemble colorful legend
        footer.append('  LOW ', colorMap.low)
        footer.append('NORMAL ', colorMap.normal)
        footer.append('HIGH', colorMap.high)

        # Add app name and version, and push to the right
        footer.append(appName.rjust(width - len(str(footer)) - 2))
        footer.end = ''

        return footer

    @staticmethod
    def _make_progressbar(console, refreshRate=2):
        """Initialize progress bar object"""
        return Progress(
            TextColumn('[progress.description]{task.description}'),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True,
            refresh_per_second=refreshRate,
        )

    @staticmethod
    def _make_statusbar(console, msg=None):
        """Initialize 'status' bar object"""
        msg = msg if msg is not None else STATUS_LBL_WAIT
        return Status(msg, console=console, spinner='dots')

    # fmt: off
    @staticmethod
    def _render_table(data, labelsOnly=False):
        """Make a new table

        This is a beefy function and (re-)renders the whole table
        on each update so that we get that real-time update feel.

        Args:
            data:
                'list' of data rows, each with a specific data set render
            labelsOnly:
                'bool' if 'True' then we only render labels and no data

        Returns:
            'Table' with data
        """

        def _prep_currval_str(data, labelsOnly=False):
            """Prep string for displaying current/last data point

            This is a formatted string with a data value and unit of
            measure. The largest value will be 4 digits + 2 decimals.
            We also want values to be right-justfied and align on the
            decimal point.

            -->|        |<--
               |12345678|
            ---|--------|---
               |1,234.56|      <- Need min 8 char width for data values
               |    1.23|

            NOTE: We display '--' if value is 'None' and status is 'ok' 
                as that represents a 'missing' value. But we display 
                'ERROR' if value is 'None' and status is not 'ok' as
                that indicates an invalid value. Both cases are shown
                as gaps in sparkline graph.   
            
            Args:
                data:
                    'dict' with data point value and attributes
                labelsOnly:
                    'bool' if 'True' then we do not generate 'current value' string

            Returns:
                'Text' object with formatted 'current value'
            """
            text = Text()
            dirChar = CHAR_DIR_DEF

            if labelsOnly or (data['dataPt'] is None and data['dataPtOK']):
                text.append(f"{dirChar} {VAL_BLANK_STR:>8} {data['unit']}", COLOR_DEF)
            elif data['dataPt'] is None and not data['dataPtOK']:
                text.append(f"{dirChar} {VAL_ERROR_STR:>8}", COLOR_ERROR)
            else:
                if data['dataPtDelta'] > 0:
                    dirChar = CHAR_DIR_UP
                elif data['dataPtDelta'] < 0:
                    dirChar = CHAR_DIR_DWN
                else:
                    dirChar = CHAR_DIR_EQ

                text.append(
                    f"{dirChar} {data['dataPt']:>8,.2f} {data['unit']}",
                    data['dataPtColor']
                )

            return text

        def _prep_sparkline_str(data, labelsOnly):
            """Prep sparkline graph string

            NOTE: 'sparklines' library will return string with ANSI color 
                codes when used with 'termcolors' library.

            Args:
                data:
                    'dict' with data point value and attributes
                labelsOnly:
                    'bool' if 'True' then we do not generate 'current value' string

            Returns:
                'Text' object with formatted 'current value'
            """
            if labelsOnly or not data['sparkData']:
                return ''
            else:
                return Text.from_ansi(
                    sparklines(
                        data['sparkData'], 
                        emph=data['sparkColors'], 
                        num_lines=1, 
                        minimum=data['sparkMinMax'][0],
                        maximum=data['sparkMinMax'][1]
                    )[-1], 
                    justify="center"
                )

        # Build a table
        table = Table(
            show_header=True,
            show_footer=False,
            show_edge=True,
            show_lines=True,
            expand=True,
            box=box.SQUARE_DOUBLE_HEAD,
        )
        table.add_column(
            Text('Description', justify='center'),
            # ratio=1,
            width=12,
            no_wrap=True,
            overflow='crop',
        )
        table.add_column(
            Text('Current', justify='center'), 
            # ratio=1, 
            width=16, 
            no_wrap=True, 
            overflow='crop'
        )
        table.add_column(
            Text('History', justify='center'),
            # ratio=4,
            min_width=12,
            no_wrap=True,
            overflow='crop',
        )

        # Render rows with/without data
        if data:
            for row in data:
                table.add_row(
                    row['label'],                           # 1st col: label
                    _prep_currval_str(row, labelsOnly),     # 2nd col: current value
                    _prep_sparkline_str(row, labelsOnly)    # 3rd col: sparkline
                )
        else:
            table.add_row('', '', '')

        return table
    # fmt: on

    def initialize(self, appNameLong, appNameShort, appVer, dataRows, enable=True):
        """Initialize main UI
        
        This method will create the base UI with all components (e.g. logo), 
        table, status fields, etc.). But there will not be any data.

        Also, the layout will depend on the width of the console. If the console
        is not wide enough, then the items will be stacked in a single column.

        Args:
            appNameLong: used for footer
            appNameShort: used for fancy logo
            appVer: app version displayed in fancy logo and footer
            dataRows: table rows with labels
            enable: 
        """
        # Get dimensions of screen/console 
        # console = Console()
        conWidth, conHeight = self._console.size

        # Is the terminal window big enough to hold the layout? Or does
        # user not want UI? If not, then we're done.
        if not enable or conWidth < APP_1COL_MIN_WIDTH or conHeight < APP_MIN_CLI_HEIGHT:
            return

        # Create fancy logo
        logo = Logo(
            int(conWidth * 2 / 3) if (conWidth >= APP_2COL_MIN_WIDTH) else conWidth,
            appNameLong,
            appNameShort,
            appVer,
        )

        # fmt: off
        # Calculate table 'size' (i.e. height in rows)
        #
        #  1  ---------      <-- divider
        #  2  HEADER ROW     <-- column header         
        #  3  ---------
        #  4  DATA ROW 1     <-- data row 1
        #  5  ---------
        #  6  DATA ROW 1     <-- data row 2
        #  7  ---------
        #
        #  size = (<num data rows> + <1 header row>) * 2 + 1
        #
        tblSize = ((len(dataRows) + 1) * 2) + 1
        # fmt: on

        # If terminal window is wide enough, then split 
        # header row and show fancy logo ...
        if conWidth >= APP_2COL_MIN_WIDTH:
            self._layout.split(
                Layout(name='header', size=(logo.rows + 1)),
                Layout(name='main', size=tblSize),
                Layout(name='footer'),
            )
            self._layout['header'].split_row(
                Layout(name='logo', ratio=2), 
                Layout(name='action')
            )
        # ... else stack all panels without fancy logo
        else:
            self._layout.split(
                Layout(name='logo', size=(logo.rows + 1), visible=(logo.rows > 1)),
                Layout(name='action', size=5),
                Layout(name='main', size=tblSize),
                Layout(name='footer'),
            )

        self._layout['action'].split(
            Layout(name='actHdr', size=1),
            Layout(name='actNextUpld', size=1),
            Layout(name='actLastUpld', size=1),
            Layout(name='actNumUpld', size=1),
            Layout(name='actCurrent', size=1),
        )

        # Display fancy logo
        if logo.rows > 1:
            self._layout['logo'].update(logo)

        self._layout['actHdr'].update(Rule(title=self.statusHdr, style=COLOR_DEF, end=''))
        self._layout['actNextUpld'].update(Text(f'{self.statusLblNext}--:--:--'))
        self._layout['actLastUpld'].update(Text(f'{self.statusLblLast}--:--:--'))
        self._layout['actNumUpld'].update(Text(f'{self.statusLblTotUpld}-'))
        self._layout['actCurrent'].update(BaseUI._make_statusbar(self._console))

        # Display main row with data table
        self._layout['main'].update(BaseUI._render_table(dataRows, True))

        # Display footer row
        self._layout['footer'].update(BaseUI._make_footer(logo.plain, conWidth))

        # Update properties for this object ... and then we're done
        self._conWidth = conWidth
        self._conHeight = conHeight
        self._active = True
        self.logo = logo

    def update_data(self, data):
        """Update table with data"""
        if self._active:
            self._layout['main'].update(BaseUI._render_table(data))

    def update_upload_num(self, num, maxNum=0):
        """Update 'upload' number(s)"""
        if self._active:
            maxNumStr = f"/{maxNum}" if maxNum > 0 else ''
            self._layout['actNumUpld'].update(Text(
                f"{self.statusLblTotUpld}{num}{maxNumStr}",
                style=COLOR_DEF
            ))

    def update_upload_next(self, nextTime):
        """Update time for next upload"""
        if self._active:
            self._layout['actNextUpld'].update(Text(
                f"{self.statusLblNext}{self._make_time_str(nextTime)}",
                style=COLOR_DEF
            ))

    def update_upload_last(self, lastTime, lastStatus=STATUS_OK):
        """Update time for last upload"""
        if self._active:
            text = Text()
            text.append(
                f"{self.statusLblLast}{self._make_time_str(lastTime)} ",
                style=COLOR_DEF
            )

            if lastStatus == STATUS_OK:
                text.append('[OK]', style=COLOR_OK)
            else:
                text.append('[Error]', style=COLOR_ERROR)

            self._layout['actLastUpld'].update(text)

    def update_upload_status(self, lastTime, lastStatus, nextTime, numUploads, maxUploads=0):
        """Update all 'status' values"""
        if self._active:
            self.update_upload_next(nextTime)
            self.update_upload_last(lastTime, lastStatus)
            self.update_upload_num(numUploads, maxUploads)

    def update_action(self, actMsg=None):
        """Update current 'action' status"""
        if self._active:
            msgStr = STATUS_LBL_WAIT if actMsg is None else actMsg
            self._layout['actCurrent'].update(self._make_statusbar(self._console, msgStr))

    def update_progress(self, progUpdate=None, progMsg=None):
        """Update progress basr"""
        if self._active:
            if progUpdate is None or self._progBar is None:
                msgStr = STATUS_LBL_WAIT if progMsg is None else progMsg
                self._progBar = self._make_progressbar(self._console)
                self._progTaskID = self._progBar.add_task(description=msgStr, total=MAX_PROGBAR)
                self._layout['actCurrent'].update(self._progBar)
            else:
                self._progBar.update(self._progTaskID, completed=progUpdate) # type: ignore
                # assert False

    def rule(self, *args, **kwargs):
        """Wrapper for Rich 'rule' function"""
        self._console.rule(*args, **kwargs)


# =========================================================
#                    M O D U L E   D E M O
# =========================================================
if __name__ == '__main__':
    print('MODULE DEMO')