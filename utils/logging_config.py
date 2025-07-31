# utils/logging_config.py

'''
Set up for logging --> Basic setup, with generic output.

Can be adjusted per log level manually.
'''

import logging

def setup_logging(level=logging.INFO, fmt="%(asctime)s [%(levelname)s] %(message)s"):
    logging.basicConfig(level=level, format=fmt)
