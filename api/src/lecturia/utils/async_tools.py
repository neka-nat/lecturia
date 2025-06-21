import asyncio
from collections.abc import Awaitable, Iterable
from typing import TypeVar


_T = TypeVar("_T")


async def gather_limited(
    coroutines: Iterable[Awaitable[_T]],
    max_parallel: int | None = None,
) -> list[_T]:
    """
    asyncio.gather の簡易ラッパー。
    与えられたコルーチンを max_parallel だけ同時実行しながら
    結果を元の順序で返す。

    max_parallel = None の場合は通常の asyncio.gather と等価。
    """
    if max_parallel is None or max_parallel <= 0:
        return await asyncio.gather(*coroutines)

    semaphore = asyncio.Semaphore(max_parallel)

    async def _wrap(coro: Awaitable[_T]) -> _T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*[_wrap(c) for c in coroutines])
