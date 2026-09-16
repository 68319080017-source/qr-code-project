from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime
import json
import asyncio

from app.database.connection import async_session_maker
from app.models.log import ActivityLog

class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We process the request first
        response = await call_next(request)
        
        # Only log mutating actions for APIs, or specific important GET requests
        if request.url.path.startswith("/api/v1") and request.method in ["POST", "PUT", "DELETE"]:
            # Run the logging task in background so we don't delay the response
            # Note: request.client might be None in some deployment setups
            ip_address = request.client.host if request.client else None
            browser = request.headers.get("user-agent", "Unknown")
            action = f"{request.method} {request.url.path}"
            
            # Create task to log
            asyncio.create_task(self.log_activity(action, ip_address, browser))
            
        return response

    async def log_activity(self, action: str, ip_address: str, browser: str):
        async with async_session_maker() as session:
            # Note: Extracting user_id usually requires accessing request state if set by auth middleware.
            # For simplicity in middleware, user_id is set to None if we can't extract it.
            log_entry = ActivityLog(
                action=action,
                ip_address=ip_address,
                browser=browser,
            )
            session.add(log_entry)
            await session.commit()
