"""f451 Labs Common Logger module.

The f451 Labs Common Logger module encapsulates the default 
Python 'Logging' class and adds a few more features that are 
commonly used in f451 Labs projects.

How to use:
    logger = Logger()
    logger = Logger(logLvl=logging.ERROR, logFile="path/to/mylogfile.log")

TODO:
 - add more/better tests
"""

import logging
import json

from rich.pretty import pprint

__all__ = [
    'Logger',
    'DEF_LOG_NAME',
    'LOG_NOTSET',
    'LOG_DEBUG',
    'LOG_INFO',
    'LOG_WARNING',
    'LOG_ERROR',
    'LOG_CRITICAL',
    'KWD_LOG_NAME',
    'KWD_LOG_LEVEL',
    'KWD_LOG_FILE',
]


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DEF_LOG_NAME = 'f451-Log'  # Default logger name

LOG_NOTSET = 0
LOG_DEBUG = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_ERROR = 40
LOG_CRITICAL = 50


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_LOG_NAME = 'LOGNAME'
KWD_LOG_LEVEL = 'LOGLVL'
KWD_LOG_FILE = 'LOGFILE'


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class Logger:
    """f451 Labs core Logger class.

    This class standardizes and simplifies logging across f451 Labs projects
    by wrapping the default Python 'logging' module/class. It also includes
    the 'pprint' for displaying debug messages.

    NOTE: attributes follow same naming convention as used
    in the 'settings.toml' file. This makes it possible to pass
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myLogger = Logger()                 # Only use default values
        myLogger = Logger(config)           # Use values from 'config'
        myLogger = Logger(key=val)          # Use val
        myLogger = Logger(config, key=val)  # Use values from 'config' and also use 'val'

    Attributes:
        LOGNAME:    Logger name as 'str'
        LOGLVL:     Log level as 'int'
        LOGFILE:    Log file as 'str' or 'Path' object

    Methods:
        set_log_level:  Set/update log level after initialization
        set_log_file:   Set/update log file after initialization
        debug:          Print debug message to stdout.
        log:            Write log message/data at any log level
        log_debug:      Write log message/data at 'debug' level
        log_info:       Write log message/data at 'info' level
        log_warning:    Write log message/data at 'warning' level
        log_error:      Write log message/data at 'error' level
    """

    def __init__(self, *args, **kwargs):
        """Initialize logger

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
        self._LOG = self._init_logger(**settings)

    @staticmethod
    def _init_file_handler(logLvl, logFile):
        fileHandler = logging.FileHandler(logFile)
        fileHandler.setLevel(logLvl)
        fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        return fileHandler

    @staticmethod
    def _init_stream_handler(logLvl):
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logLvl)
        streamHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        return streamHandler

    def _init_logger(self, **kwargs):
        """Initialize Logger

        We always initialize the logger with a stream
        handler. But file handler is only created if
        a file name has been provided in settings.

        Args:
            kwargs:
                Core settings as key-value pairs in 'dict'

        Returns:
            Initialized 'logger' object
        """
        logName = kwargs.get(KWD_LOG_NAME, DEF_LOG_NAME)
        logLvl = kwargs.get(KWD_LOG_LEVEL, logging.NOTSET)
        logFile = kwargs.get(KWD_LOG_FILE)

        logger = logging.getLogger(logName)
        logger.setLevel(logLvl)

        if logFile:
            logger.addHandler(self._init_file_handler(logLvl, logFile))

        logger.addHandler(self._init_stream_handler(logLvl))

        return logger

    def set_log_level(self, logLvl):
        """Set/update log level after initialization."""
        self._LOG.setLevel(logLvl)

        for handler in self._LOG.handlers[:]:
            handler.setLevel(logLvl)

    def set_log_file(self, logLvl, logFile):
        """Set/update log file after initialization.

        Based on solution found here:
        https://stackoverflow.com/questions/13839554/how-to-change-filehandle-with-python-logging-on-the-fly-with-different-classes-a
        """
        # Remove any existing file handlers
        for handler in self._LOG.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self._LOG.removeHandler(handler)

        # Add new file handler
        self._LOG.addHandler(self._init_file_handler(logLvl, logFile))

    def debug(self, val, strict=True):
        """Print debug message to stdout.

        This is a wrapper of pprint.pprint().

        Args:
            val: Value to be 'pretty' printed
            strict: If 'True', then values are printed as-is
        """
        if isinstance(val, dict) and not strict:
            pprint(json.dumps(val, indent=4), expand_all=True)
        else:
            pprint(val, expand_all=True)

    def log(self, msg, lvl=logging.DEBUG):
        """Log message/data

        Thisn is a wrapper of Logger.log().

        Args:
            msg: Log message as 'str'
            lvl: Logging level as 'int'. Default is 'logging.DEBUG'
        """
        self._LOG.log(lvl, msg)

    def log_debug(self, msg):
        """Wrapper of Logger.debug()

        Args:
            msg: Log message as 'str'
        """
        self._LOG.debug(msg)

    def log_info(self, msg):
        """Wrapper of Logger.info()

        Args:
            msg: Log message as 'str'
        """
        self._LOG.info(msg)

    def log_warning(self, msg):
        """Wrapper of Logger.warning()

        Args:
            msg: Log message as 'str'
        """
        self._LOG.warning(msg)

    def log_error(self, msg):
        """Wrapper of Logger.error()

        Args:
            msg: Log message as 'str'
        """
        self._LOG.error(msg)


# =========================================================
#                    M O D U L E   D E M O
# =========================================================
if __name__ == '__main__':
    # Initialize Logger
    logger = Logger(LOGLVL=logging.INFO)

    print('\n====== [Demo of f451 Labs Logger module] ======')
    print('Showing log message:')
    logger.log('Hello world!', logging.INFO)

    print('\nShowing PrettyPrint:')
    logger.debug('Hello world!')

    print('=============== [End of Demo] =================\n')
