from loguru import logger

logFile = "logs/app.log"
logger.add(logFile, rotation="10 MB")
logger.remove(0)    # disable output to stderr


def debug(msg):
    logger.debug(msg)


def info(msg):
    logger.info(msg)


def warning(msg):
    logger.warning(msg)


def error(msg):
    logger.error(msg)


def critical(msg):
    logger.critical(msg)
