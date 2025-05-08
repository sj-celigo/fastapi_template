import time
import logging
import json
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


# Get logger
logger = logging.getLogger("app.middleware")


# Custom structured logging functions
def log_request_event(message, **kwargs):
    """Log request events with structured data."""
    # Add trace context if available
    span_context = trace.get_current_span().get_span_context()
    if span_context and span_context.is_valid:
        kwargs["trace_id"] = format(span_context.trace_id, "032x")
        kwargs["span_id"] = format(span_context.span_id, "016x")
    
    logger.info(message, extra=kwargs)


def log_error_event(message, **kwargs):
    """Log error events with structured data."""
    # Add trace context if available
    span_context = trace.get_current_span().get_span_context()
    if span_context and span_context.is_valid:
        kwargs["trace_id"] = format(span_context.trace_id, "032x")
        kwargs["span_id"] = format(span_context.span_id, "016x")
    
    logger.error(message, extra=kwargs)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.tracer = trace.get_tracer("fastapi.request")
        self.propagator = TraceContextTextMapPropagator()

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Extract tracing context from request headers if available
        context = {}
        self.propagator.extract(context, request.headers)
        
        # Start a new span for this request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
            context=context,
        ) as span:
            # Add request attributes to span
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.request_id", request_id)
            span.set_attribute("http.client_ip", request.client.host if request.client else "unknown")
            
            # Log request with structured data
            log_request_event(
                "Request started",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                client_ip=request.client.host if request.client else "unknown"
            )
            
            # Measure request processing time
            start_time = time.time()
            
            # Process request
            try:
                response = await call_next(request)
                process_time = time.time() - start_time
                
                # Add request_id to response headers
                response.headers["X-Request-ID"] = request_id
                status_code = response.status_code
                
                # Add response attributes to span
                span.set_attribute("http.status_code", status_code)
                span.set_attribute("http.duration_ms", process_time * 1000)
                
                # Log response with structured data
                log_request_event(
                    "Request completed",
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    duration_sec=round(process_time, 3)
                )
                
                return response
            except Exception as e:
                process_time = time.time() - start_time
                
                # Record exception in span
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                
                # Log error with structured data
                log_error_event(
                    "Request failed",
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    error=str(e),
                    duration_sec=round(process_time, 3)
                )
                raise 