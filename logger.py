import logging
import config

from logging.handlers import TimedRotatingFileHandler

def configure_logger():
    """
    Abstract logger setup
    """
    logging.root.setLevel(config.LOGGER_LEVEL)
    
    file_handler = TimedRotatingFileHandler(config.LOG_FILE_PATH, when="W0", interval=7, backupCount=4)
    stream_handler = logging.StreamHandler()
    
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] [%(identifier)s] %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
 

def get_logger_with_context(identifier):
    extra = {
        "identifier" : identifier
    }
    return logging.LoggerAdapter(logging.getLogger(__name__), extra)  