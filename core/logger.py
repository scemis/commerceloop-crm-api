# core/logger.py
from loguru import logger
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = datetime.now().strftime("%d_%m_%Y") + "log.txt"
log_path = os.path.join(LOG_DIR, log_filename)

# убрать дефолтный sink
logger.remove()

# писать в файл; новый файл каждый день
logger.add(
    log_path,
    rotation="00:00",        # новый файл в 00:00
    retention="30 days",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

__all__ = ["logger"]