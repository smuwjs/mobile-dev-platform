"""WebSocket support for real-time task progress updates."""

import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from starlette.routing import Route, WebSocketRoute


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast(self, message: dict, user_id: str | None = None):
        """Broadcast a message to all connections or specific user."""
        if user_id:
            connections = self.active_connections.get(user_id, [])
            for connection in connections:
                await self.send_personal_message(message, connection)
        else:
            for user_connections in self.active_connections.values():
                for connection in user_connections:
                    await self.send_personal_message(message, connection)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    """Handle WebSocket connections for real-time updates."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(message, websocket, user_id)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def handle_client_message(
    message: dict,
    websocket: WebSocket,
    user_id: str
):
    """Handle incoming client messages."""
    msg_type = message.get("type")

    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    elif msg_type == "subscribe":
        project_id = message.get("project_id")
        if project_id:
            await websocket.send_json({
                "type": "subscribed",
                "project_id": project_id
            })
    elif msg_type == "unsubscribe":
        await websocket.send_json({"type": "unsubscribed"})


def broadcast_task_update(task_id: str, task_data: dict):
    """Broadcast task status update to all connected clients."""
    asyncio.create_task(
        manager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "data": task_data,
        })
    )


def broadcast_task_progress(task_id: str, progress: int, status: str):
    """Broadcast task progress update."""
    asyncio.create_task(
        manager.broadcast({
            "type": "task_progress",
            "task_id": task_id,
            "progress": progress,
            "status": status,
        })
    )


def broadcast_task_completed(task_id: str, result: Any = None, error: str | None = None):
    """Broadcast task completion."""
    asyncio.create_task(
        manager.broadcast({
            "type": "task_completed",
            "task_id": task_id,
            "result": result,
            "error": error,
        })
    )


def broadcast_execution_update(
    task_id: str,
    execution_id: str,
    status: str,
    result: Any = None,
    error: str | None = None
):
    """Broadcast execution status update."""
    asyncio.create_task(
        manager.broadcast({
            "type": "execution_update",
            "task_id": task_id,
            "execution_id": execution_id,
            "status": status,
            "result": result,
            "error": error,
        })
    )


routes = [
    WebSocketRoute("/ws", websocket_endpoint),
]
