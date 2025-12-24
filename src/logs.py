import logging

import logtail

logger = logging.getLogger("todos")

LOG_FORMAT_INFO = (
    "%(asctime)s [%(levelname)s]: %(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
)

logger.setLevel(logging.INFO)

logtail_handler = logtail.LogtailHandler(
    source_token="aFrmjSwDaaviZ1TSEL7yVmmS",
    host="s1612562.eu-nbg-2.betterstackdata.com",
)

logtail_handler.setFormatter(logging.Formatter(LOG_FORMAT_INFO))

logger.addHandler(logtail_handler)
