"""
WebSocket connection manager for real-time voice conversations
"""

from fastapi import WebSocket
from typing import List, Dict, Optional
import json
import uuid
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and sessions"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, WebSocket] = {}
        self.connection_sessions: Dict[WebSocket, str] = {}
        self.session_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection and create session"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Create new session
        session_id = str(uuid.uuid4())
        self.session_connections[session_id] = websocket
        self.connection_sessions[websocket] = session_id
        
        # Initialize session metadata
        self.session_metadata[session_id] = {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "turn_count": 0,
            "language": "omani-arabic",
            "is_crisis_session": False,
            "emotional_state": "neutral",
            "cultural_context": {}
        }
        
        logger.info(f"New connection established: {session_id}")
        return session_id
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        session_id = self.connection_sessions.get(websocket)
        if session_id:
            del self.session_connections[session_id]
            del self.connection_sessions[websocket]
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
            logger.info(f"Connection closed: {session_id}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
            
            # Update session activity
            session_id = self.connection_sessions.get(websocket)
            if session_id:
                self.session_metadata[session_id]["last_activity"] = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all active connections"""
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.disconnect(connection)
    
    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        """Get session ID for WebSocket connection"""
        return self.connection_sessions.get(websocket)
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict]:
        """Get metadata for session"""
        return self.session_metadata.get(session_id)
    
    def update_session_metadata(self, session_id: str, updates: Dict):
        """Update session metadata"""
        if session_id in self.session_metadata:
            self.session_metadata[session_id].update(updates)
            self.session_metadata[session_id]["last_activity"] = datetime.utcnow()
    
    def mark_crisis_session(self, session_id: str):
        """Mark session as crisis intervention"""
        self.update_session_metadata(session_id, {"is_crisis_session": True})
    
    def increment_turn_count(self, session_id: str):
        """Increment conversation turn count"""
        metadata = self.get_session_metadata(session_id)
        if metadata:
            metadata["turn_count"] += 1
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """Remove inactive sessions"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        inactive_sessions = []
        for session_id, metadata in self.session_metadata.items():
            if metadata["last_activity"] < cutoff_time:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            websocket = self.session_connections.get(session_id)
            if websocket:
                self.disconnect(websocket)

class WebSocketManager:
    """Main WebSocket manager instance"""
    
    def __init__(self):
        self.manager = ConnectionManager()
        # Cleanup task will be started when an event loop is running
    
    def start_cleanup_task(self):
        """Start background task for cleaning up inactive sessions"""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(300)  # Run every 5 minutes
                self.manager.cleanup_inactive_sessions()
        
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(cleanup_loop())
            logger.info("WebSocket cleanup task started")
        except RuntimeError:
            # No running loop; caller should invoke this when loop is active
            logger.warning("Deferred starting WebSocket cleanup task: no running event loop")
    
    async def connect(self, websocket: WebSocket) -> str:
        """Connect new WebSocket"""
        return await self.manager.connect(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket"""
        self.manager.disconnect(websocket)
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send personal message"""
        await self.manager.send_personal_message(message, websocket)
    
    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        """Get session ID"""
        return self.manager.get_session_id(websocket)
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict]:
        """Get session metadata"""
        return self.manager.get_session_metadata(session_id)
    
    def update_session_metadata(self, session_id: str, updates: Dict):
        """Update session metadata"""
        self.manager.update_session_metadata(session_id, updates)
    
    def mark_crisis_session(self, session_id: str):
        """Mark crisis session"""
        self.manager.mark_crisis_session(session_id)
    
    def increment_turn_count(self, session_id: str):
        """Increment turn count"""
        self.manager.increment_turn_count(session_id)
