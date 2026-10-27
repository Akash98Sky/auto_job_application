from ..logger_config import get_logger


class BaseAgent:
    """
    Standard Base Agent class representing the core interface and shared attributes
    for all autonomous agents in the auto_job_application system.

    Attributes:
        logger (logging.Logger): An initialized logger instance named after the inheriting class.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Initialized agent: {self.__class__.__name__}")

    async def close(self) -> None:
        """
        Asynchronously closes active resources, releases file locks,
        and shuts down browser instances or database connections held by the agent.
        """
        self.logger.debug(f"No custom teardown defined for: {self.__class__.__name__}")
