# SPDX-License-Identifier: MIT
"""
Copy from https://github.com/sysid/sse-starlette/blob/main/sse_starlette/event.py
"""

import io
import json
import re
from typing import Any


class ServerSentEvent:
    """
    Helper class to format data for Server-Sent Events (SSE).
    """

    _LINE_SEP_EXPR = re.compile(r"\r\n|\r|\n")
    DEFAULT_SEPARATOR = "\r\n"

    def __init__(
        self,
        data: Any | None = None,
        *,
        event: str | None = None,
        id: str | None = None,
        retry: int | None = None,
        comment: str | None = None,
        sep: str | None = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self._sep = sep if sep is not None else self.DEFAULT_SEPARATOR

    def encode(self) -> bytes:
        buffer = io.StringIO()
        if self.comment is not None:
            for chunk in self._LINE_SEP_EXPR.split(str(self.comment)):
                buffer.write(f": {chunk}{self._sep}")

        if self.id is not None:
            # Clean newlines in the event id
            buffer.write("id: " + self._LINE_SEP_EXPR.sub("", self.id) + self._sep)

        if self.event is not None:
            # Clean newlines in the event name
            buffer.write(
                "event: " + self._LINE_SEP_EXPR.sub("", self.event) + self._sep
            )

        if self.data is not None:
            # Break multi-line data into multiple data: lines
            for chunk in self._LINE_SEP_EXPR.split(str(self.data)):
                buffer.write(f"data: {chunk}{self._sep}")

        if self.retry is not None:
            if not isinstance(self.retry, int):
                raise TypeError("retry argument must be int")
            buffer.write(f"retry: {self.retry}{self._sep}")

        buffer.write(self._sep)
        return buffer.getvalue().encode("utf-8")


class JSONServerSentEvent(ServerSentEvent):
    """
    Helper class to format JSON data for Server-Sent Events (SSE).
    """

    def __init__(
        self,
        data: Any | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            json.dumps(
                data,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            )
            if data is not None
            else None,
            *args,
            **kwargs,
        )


def ensure_bytes(data: bytes | dict | ServerSentEvent | Any, sep: str) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, ServerSentEvent):
        return data.encode()
    if isinstance(data, dict):
        data["sep"] = sep
        return ServerSentEvent(**data).encode()
    return ServerSentEvent(str(data), sep=sep).encode()
