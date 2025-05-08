import time
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Log request
        ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        
        logger.info(f"Request started: {method} {path} | ID: {request_id} | IP: {ip} | Params: {query_params}")
        
        # Measure request processing time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id
            status_code = response.status_code
            
            # Log response
            logger.info(
                f"Request completed: {method} {path} | ID: {request_id} | "
                f"Status: {status_code} | Time: {process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path} | ID: {request_id} | "
                f"Error: {str(e)} | Time: {process_time:.3f}s"
            )
            raise 