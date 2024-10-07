def transactional(func):
    async def wrapper(self, *args, **kwargs):
        session = getattr(self, 'session', None)

        if session is None:
            raise ValueError("Session not provided")

        if session.in_transaction():
            return await func(self, *args, **kwargs)

        async with session.begin():
            try:
                return await func(self, *args, **kwargs)
            except Exception:
                await session.rollback()
                raise

    return wrapper