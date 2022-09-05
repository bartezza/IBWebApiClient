import logging
import sys
from typing import Optional

import coloredlogs


def init_logging(default_level: str = logging.DEBUG,
                 log_format: Optional[str] = None):
    if log_format is None:
        log_format =\
            "[%(asctime)s,%(msecs)03d %(name)s %(levelname)s]  %(message)s"
    coloredlogs.install(fmt=log_format, stream=sys.stdout, level=default_level)

    # default level
    logging.getLogger("root").setLevel(default_level)

    # change logging level of libs
    loggers = {
        logging.WARNING: ["ibapi", "matplotlib"],
        logging.INFO: ["ccxt", "urllib3"]
    }
    for level, libs in loggers.items():
        for lib in libs:
            logging.getLogger(lib).setLevel(level)
