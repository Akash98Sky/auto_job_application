from browser_use import Browser

from .config import BROWSER_EXECUTABLE_PATH, BROWSER_PROFILE_DIR, BROWSER_USER_DATA_DIR

class SessionPool:
    def __init__(self):
        self._by_tenant: dict[str, Browser] = {}

    async def get_or_create(self, tenant_id: str = "default") -> Browser:
        if tenant_id not in self._by_tenant:
            b = Browser(
                executable_path=BROWSER_EXECUTABLE_PATH,
                user_data_dir=BROWSER_USER_DATA_DIR,
                profile_directory=BROWSER_PROFILE_DIR,
                args=['--disable-extensions'],
                keep_alive=True
            )
            await b.start()
            self._by_tenant[tenant_id] = b
        return self._by_tenant[tenant_id]

    async def close(self, tenant_id: str):
        b = self._by_tenant.pop(tenant_id, None)
        if b:
            await b.kill()

    async def close_all(self):
        for b in list(self._by_tenant.values()):
            await b.kill()
        self._by_tenant.clear()