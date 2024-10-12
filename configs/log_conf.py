import logging
import os
from datetime import datetime


def configure_logging():
    level = os.getenv("LOGING_LEVEL")
    mark = datetime.now()
    if not os.path.exists('log'):
        os.mkdir('log')
    if level == 'DEBUG':
        logging.basicConfig(

            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(levelname)-7s - %(message)s",  # %(module)15s:%(lineno)-3d
            # filename="log/app.log",
            # filemode="w"
            )
    else:
        file_log = logging.FileHandler('log/app.log', "a", encoding="UTF-8")
        console_out = logging.StreamHandler()
        logging.basicConfig(

            handlers=(file_log, console_out),
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(levelname)-7s - %(message)s", # %(module)15s:%(lineno)-3d
            # filename="log/app.log",
            # filemode="w"
        )
