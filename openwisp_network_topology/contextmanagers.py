import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def log_failure(action, obj):
    try:
        yield
    except Exception as e:
        msg = "Failed to perform {0} on {1}".format(action, obj.__repr__())
        logger.exception(msg)
        print(
            "{0}: {1}\nSee error log for more "
            "information\n".format(msg, e.__class__.__name__)
        )
