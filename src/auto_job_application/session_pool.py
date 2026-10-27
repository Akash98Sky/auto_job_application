import atexit

from browser_use import Browser

from .config import BROWSER_EXECUTABLE_PATH, BROWSER_PROFILE_DIR, BROWSER_USER_DATA_DIR
from .logger_config import get_logger

logger = get_logger(__name__)


class SessionPool:
    """
    Manages a thread-safe multi-tenant pool of automated browser instances
    using browser-use. Prevents runaway browser processes by pooling sessions.
    """

    def __init__(self) -> None:
        """
        Initializes the SessionPool with an empty tenant registry.
        """
        self._by_tenant: dict[str, Browser] = {}
        logger.info("SessionPool initialized successfully.")
        # Register atexit process termination to prevent background browser orphans
        atexit.register(self.close_all_sync)

    def close_all_sync(self) -> None:
        """
        Synchronously closes all active browser sessions in the pool.
        This is designed to be registered as an atexit handler to prevent
        orphaned Chromium/Edge processes when the interpreter exits.
        """
        if not self._by_tenant:
            return

        logger.info("SessionPool registering global shutdown; killing active browser processes...")
        import asyncio

        for tenant_id in list(self._by_tenant.keys()):
            b = self._by_tenant.pop(tenant_id, None)
            if b:
                try:
                    logger.info(f"Sync-killing browser session for tenant: '{tenant_id}'...")
                    try:
                        loop = asyncio.get_running_loop()
                        if loop.is_running():
                            loop.create_task(b.kill()).result()
                        else:
                            asyncio.run(b.kill())
                    except RuntimeError:
                        asyncio.run(b.kill())
                except Exception as e:
                    logger.debug(f"Sync-killing failed for tenant '{tenant_id}': {e}")
        self._by_tenant.clear()

    async def get_or_create(self, tenant_id: str = "default") -> Browser:
        """
        Retrieves an active browser instance for the tenant or creates a new one.

        Args:
            tenant_id (str, optional): A unique identifier for the tenant. Defaults to "default".

        Returns:
            Browser: An active and initialized browser-use Browser instance.
        """
        if tenant_id not in self._by_tenant:
            logger.info(f"Creating new browser session for tenant: '{tenant_id}'...")
            try:
                b = Browser(
                    executable_path=BROWSER_EXECUTABLE_PATH,
                    user_data_dir=BROWSER_USER_DATA_DIR,
                    profile_directory=BROWSER_PROFILE_DIR,
                    args=["--disable-extensions"],
                    keep_alive=True,
                )
                await b.start()
                self._by_tenant[tenant_id] = b
                logger.info(f"Browser session started for tenant: '{tenant_id}'.")
            except Exception as e:
                logger.error(f"Failed to initialize browser session for tenant '{tenant_id}': {e}")
                raise e
        return self._by_tenant[tenant_id]

    async def close(self, tenant_id: str) -> None:
        """
        Closes and terminates the browser session for a specific tenant.

        Args:
            tenant_id (str): Unique identifier of the tenant session to terminate.
        """
        b = self._by_tenant.pop(tenant_id, None)
        if b:
            logger.info(f"Closing browser session for tenant: '{tenant_id}'...")
            try:
                await b.kill()
                logger.info(f"Successfully terminated browser session for tenant: '{tenant_id}'.")
            except Exception as e:
                logger.warning(f"Error while killing browser session for tenant '{tenant_id}': {e}")

    async def close_all(self) -> None:
        """
        Closes all active browser sessions managed in the pool,
        freeing all system resources and browser processes.
        """
        logger.info("Closing all active browser sessions in SessionPool...")
        for tenant_id in list(self._by_tenant.keys()):
            await self.close(tenant_id)
        self._by_tenant.clear()
