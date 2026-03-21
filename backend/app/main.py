from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router

# WebSocket manager
from app.api.websocket import ConnectionManager

ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    from app.db.session import create_tables
    create_tables()
    yield


app = FastAPI(
    title="Mobile Dev Platform API",
    description="移动端开发管理平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await ws_manager.connect(websocket, "anonymous")
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Received: {data}")
    except Exception:
        pass


# Include API routes
app.include_router(api_v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
