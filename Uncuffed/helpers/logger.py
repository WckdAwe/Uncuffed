# Source Taken from:
# https://realpython.com/python-logging/
# https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings

import logging


def setup_logger(name, log_file, level=logging.INFO):
    # Create a custom logger
    logger = logging.getLogger(name)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('[%(levelname)s] %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


log = setup_logger('default', 'file.log', logging.DEBUG)
