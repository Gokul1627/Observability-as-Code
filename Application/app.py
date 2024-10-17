import os
import time
import random
from flask import Flask
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
import logging
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
app = Flask(__name__)

# Get Alloy endpoint from environment variable
ALLOY_ENDPOINT = os.getenv('ALLOY_ENDPOINT', 'http://alloy:4320')

# Configure resource
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "my-python-service"
})

# Configure tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_span_exporter = OTLPSpanExporter(endpoint=ALLOY_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=ALLOY_ENDPOINT)
)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

# Configure logging
logger_provider = LoggerProvider(resource=resource)
otlp_log_exporter = OTLPLogExporter(endpoint=ALLOY_ENDPOINT)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# Get logger and set handler
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create a counter metric
request_counter = meter.create_counter(
    name="request_counter",
    description="Counts the number of requests",
    unit="1",
)

# Main application logic
def process_request():
    with tracer.start_as_current_span("process_request") as span:
        # Simulate some work
        time.sleep(random.uniform(0.1, 0.5))
        
        # Record a metric
        request_counter.add(1)
        
        # Log some information
        logger.info("Request processed successfully")
        
        # Add an attribute to the span
        span.set_attribute("request.id", str(random.randint(1000, 9999)))

@app.route('/')
def handle_request():
    process_request()  # Call your request processing logic here
    return "Request processed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Keep the web server running