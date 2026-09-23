import time

from fastapi import Request


async def add_process_time(request: Request, call_next):
    """Добавляет в каждый HTTP-ответ заголовок X-Process-Time — время обработки запроса."""

    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.perf_counter() - start_time, 6))
    return response
