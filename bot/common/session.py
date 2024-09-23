import aiohttp


class SingletoneSession:
    _instance = None

    @classmethod
    async def get_session(cls):
        if cls._instance is None:
            cls._instance = aiohttp.ClientSession()
        return cls._instance

    @classmethod
    async def close_session(cls):
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
