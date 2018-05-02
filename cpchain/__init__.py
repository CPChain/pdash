import logging
import logging.config

from .utils import root_dir, config

logging.getLogger(__name__).addHandler(logging.NullHandler)
logging.config.dictConfig(config.logging.conf)
