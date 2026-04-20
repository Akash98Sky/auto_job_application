import logging
import colorlog

logger = colorlog.getLogger("job_agent")

def get_logger(name: str | None = None) -> logging.Logger:
    if name is None:
        return logger
    return logger.getChild(name)

def setup_logger():
    # Configure colorful logging
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Optional: You can explicitly configure browser_use logger
    logging.getLogger("browser_use").setLevel(logging.INFO)
    return logger
