import logging
import sys
import os


logger = logging.getLogger(__name__)

if not logger.handlers:
    app_env = os.getenv("APP_ENV")

    if app_env == "dev":
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    else:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(levelname)s: [%(filename)s:%(lineno)d] %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)