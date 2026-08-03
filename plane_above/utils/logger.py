import logging

log = logging.getLogger("plane_above")
if not log.handlers:
    log.addHandler(logging.NullHandler())
