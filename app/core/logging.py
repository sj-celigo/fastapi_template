import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.core.config import settings


# Configure OpenTelemetry
def setup_telemetry(app=None):
    """Configure OpenTelemetry tracing."""
    resource = Resource.create({"service.name": settings.PROJECT_NAME})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure exporter - in production, you might want to send to a collector
    # For simplicity, we'll use the console exporter during development
    # Alternatively, you can use OTLPSpanExporter for a production setup
    # exporter = OTLPSpanExporter(endpoint="http://collector:4318/v1/traces")
    exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Instrument FastAPI if app is provided
    if app:
        FastAPIInstrumentor.instrument_app(app)
    
    return trace.get_tracer(settings.PROJECT_NAME)


# Configure structured logging
class StructuredLogFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after parsing the log record."""
    
    def format(self, record) -> str:
        """Format the log record as JSON."""
        log_object: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        
        # Add trace context if available
        span_context = trace.get_current_span().get_span_context()
        if span_context and span_context.is_valid:
            log_object["trace_id"] = format(span_context.trace_id, "032x")
            log_object["span_id"] = format(span_context.span_id, "016x")
        
        # Add extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in ["timestamp", "level", "name", "message", "exception", "trace_id", "span_id", 
                          "args", "exc_info", "exc_text", "pathname", "filename", "module", 
                          "levelno", "levelname", "funcName", "lineno", "created", 
                          "msecs", "relativeCreated", "msg"]:
                log_object[key] = value
        
        return json.dumps(log_object)


def setup_logging():
    """Configure structured logging with OpenTelemetry context."""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredLogFormatter())
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.FileHandler(logs_dir / "app.log")
    file_handler.setFormatter(StructuredLogFormatter())
    root_logger.addHandler(file_handler)
    
    # Return the logger
    return logging.getLogger("app") 