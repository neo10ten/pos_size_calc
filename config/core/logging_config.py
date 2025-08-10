# config/core/logging_config.py

import logging
from .settings import DEBUG

'''
Set up for logging --> Basic setup, with generic output.

Can be adjusted per log level manually.
'''

LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

def configure_logging():
    logging.basicConfig(
        level      = LOG_LEVEL,
        format     = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt    = "%Y-%m-%d %H:%M:%S",
        handlers   = [logging.StreamHandler()]
    )