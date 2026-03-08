from __future__ import annotations

import asyncio
import json
import logging

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        if not self._connections:
            return

        stale: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)

        for connection in stale:
            self._connections.discard(connection)


manager = WebSocketManager()


async def redis_listener() -> None:
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(settings.feedback_event_channel)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                try:
                    payload = json.loads(message["data"])
                except json.JSONDecodeError:
                    payload = {"event": "raw", "payload": message["data"]}
                await manager.broadcast(payload)
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        logger.info("Redis listener cancelled")
        raise
    finally:
        await pubsub.unsubscribe(settings.feedback_event_channel)
        await pubsub.aclose()
        await redis_client.aclose()
