import logging
from config import LOG_FILE, LOG_LEVEL


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=getattr(logging, LOG_LEVEL),
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    return logging.getLogger(__name__)
