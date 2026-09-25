# app/io.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import uuid
from typing import AsyncIterable, AsyncIterator

import aiofiles
import aiofiles.os
import aiofiles.ospath

from app.constants import FILE_CHUNK_SIZE_BYTES


async def listdir(path: str) -> list[str]:
    """Return the entry names contained in a directory."""
    return list(await aiofiles.os.listdir(path))


async def isfile(path: str) -> bool:
    """Return whether the path points to a regular file."""
    return await aiofiles.ospath.isfile(path)


async def isdir(path: str) -> bool:
    """Return whether the path points to a directory."""
    return await aiofiles.ospath.isdir(path)


async def ismount(path: str) -> bool:
    """Return whether the path is a mount point."""
    return await aiofiles.ospath.ismount(path)


async def mktree(path: str) -> None:
    """
    Create a directory together with its missing parents and persist
    the directory entry updates. An existing directory is left as is,
    and every level actually created is fsynced through its parent.
    """
    created = await asyncio.to_thread(_makedirs_sync, path)

    for directory in reversed(created):
        await _fsync_dir(_get_parent_dir(directory))


async def rmtree(path: str) -> None:
    """
    Remove a directory with the files it contains and persist the
    directory entry updates. A missing directory is left as is.
    """
    if not await isdir(path):
        return

    for name in await listdir(path):
        child = os.path.join(path, name)

        if await isdir(child):
            await rmtree(child)
        else:
            await delete(child)

    await _rmdir(path)


async def write(
    destination: str,
    data: bytes | bytearray | memoryview,
) -> None:
    """
    Atomically write in-memory bytes to destination. Data is chunked,
    written to a temporary file, then flushed, fsynced, atomically
    replaced, and the parent directory is fsynced.
    """
    async def data_iter() -> AsyncIterator[bytes]:
        view = memoryview(data)
        for offset in range(0, len(view), FILE_CHUNK_SIZE_BYTES):
            yield bytes(view[offset:offset + FILE_CHUNK_SIZE_BYTES])

    await _atomic_write_stream(data_iter(), destination)


async def read(path: str) -> bytes:
    """
    Read the whole file asynchronously in chunks. Data is read
    incrementally and accumulated into a single bytes object returned
    to the caller.
    """
    result = bytearray()

    async for chunk in iter_read(path):
        result.extend(chunk)

    return bytes(result)


async def delete(path: str) -> None:
    """
    Delete a file and persist the directory entry update. The file
    is unlinked and the parent directory is fsynced if the deletion
    succeeds.
    """
    try:
        await asyncio.to_thread(os.unlink, path)
    except FileNotFoundError:
        return

    await _fsync_dir(_get_parent_dir(path))


async def iter_read(
    path: str,
    chunk_size: int = FILE_CHUNK_SIZE_BYTES,
) -> AsyncIterator[bytes]:
    """
    Read a file asynchronously and yield chunks. The file remains open
    during iteration and data is yielded without loading the whole file
    into memory.
    """
    async with aiofiles.open(path, mode="rb") as file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk


async def _atomic_write_stream(
    data: AsyncIterable[bytes],
    destination: str,
) -> None:
    """
    Atomically write a byte stream to destination. Data is written to
    a temporary file, then flushed, fsynced, atomically replaced, and
    the parent directory is fsynced.
    """
    parent_directory = _get_parent_dir(destination)
    temporary_path = _build_temp_path(destination)

    try:
        async with aiofiles.open(temporary_path, mode="wb") as file:
            async for chunk in data:
                await file.write(chunk)

            await file.flush()
            await asyncio.to_thread(os.fsync, file.fileno())

        await asyncio.to_thread(os.replace, temporary_path, destination)
        await _fsync_dir(parent_directory)

    except Exception:
        try:
            await asyncio.to_thread(os.unlink, temporary_path)
        except FileNotFoundError:
            pass
        raise


def _makedirs_sync(path: str) -> list[str]:
    """
    Create a directory tree and return the directories that were
    missing, ordered from the deepest to the shallowest one.
    """
    created: list[str] = []
    cursor = os.path.abspath(path)

    while not os.path.isdir(cursor):
        created.append(cursor)
        parent = os.path.dirname(cursor)

        if parent == cursor:
            break

        cursor = parent

    os.makedirs(path, exist_ok=True)

    return created


def _build_temp_path(destination: str) -> str:
    """
    Build a unique temporary path next to destination. The file
    is created in the same directory to allow atomic replace.
    """
    parent_directory = _get_parent_dir(destination)
    filename = os.path.basename(destination)
    temporary_name = f".{filename}.{uuid.uuid4().hex}.tmp"
    return os.path.join(parent_directory, temporary_name)


def _get_parent_dir(path: str) -> str:
    """
    Return the parent directory of a path. Paths without a directory
    resolve to the current directory.
    """
    parent_directory = os.path.dirname(path)
    return parent_directory or "."


async def _fsync_dir(path: str) -> None:
    """
    Fsync a directory to persist metadata changes. Used after create,
    replace, and delete operations.
    """
    directory_fd = await asyncio.to_thread(os.open, path, os.O_RDONLY)
    try:
        await asyncio.to_thread(os.fsync, directory_fd)
    finally:
        await asyncio.to_thread(os.close, directory_fd)


async def _rmdir(path: str) -> None:
    """Remove an empty directory and persist the directory entry update."""
    parent = _get_parent_dir(path)
    await aiofiles.os.rmdir(path)
    await _fsync_dir(parent)
