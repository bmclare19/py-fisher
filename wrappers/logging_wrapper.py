import logging
from functools import partial, partialmethod
from app_config import config

logging.TRACE = 5
logging.addLevelName(logging.TRACE, 'TRACE')
logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
logging.trace = partial(logging.log, logging.TRACE)

log_level = {
    'ERROR': logging.ERROR,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'TRACE': logging.TRACE
}

logging.basicConfig(
    level=log_level.get(config['log_lvl']),
    format='%(asctime)s.%(msecs)03d|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

error = logging.error
info = logging.info
debug = logging.debug
trace = logging.trace