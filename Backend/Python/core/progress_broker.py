"""Lightweight in-process pubsub for dream generation progress.

The LangGraph pipeline runs synchronously inside the FastAPI process.
Cenedril's image/video agents call `publish(dream_id, event)` as work
progresses; the FastAPI WS handler subscribes via `subscribe(dream_id)`
and forwards events to the React UI.

Thread-safe: agents may run on a worker thread while the WS handler is
on the asyncio event loop. Subscribers receive events through a
`queue.Queue` and read them with `asyncio.to_thread`.
"""

from __future__ import annotations

import queue
import threading
from typing import Any

_lock = threading.Lock()
_subscribers: dict[str, list[queue.Queue]] = {}


def publish(dream_id: str, event: dict[str, Any]) -> None:
    if not dream_id:
        return
    with _lock:
        subs = list(_subscribers.get(dream_id, ()))
    for q in subs:
        try:
            q.put_nowait(event)
        except queue.Full:
            pass


def subscribe(dream_id: str) -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=256)
    with _lock:
        _subscribers.setdefault(dream_id, []).append(q)
    return q


def unsubscribe(dream_id: str, q: queue.Queue) -> None:
    with _lock:
        subs = _subscribers.get(dream_id)
        if not subs:
            return
        try:
            subs.remove(q)
        except ValueError:
            pass
        if not subs:
            _subscribers.pop(dream_id, None)
