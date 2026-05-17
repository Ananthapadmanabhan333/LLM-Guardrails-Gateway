from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from app.config import settings

_tracer = None
_tracer_provider = None


def setup_tracing():
    global _tracer, _tracer_provider

    if not settings.enable_otel_tracing:
        from opentelemetry.sdk.trace import TracerProvider as SimpleProvider
        _tracer_provider = SimpleProvider()
        trace.set_tracer_provider(_tracer_provider)
        _tracer = trace.get_tracer(settings.otel_service_name)
        return

    resource = Resource.create({
        "service.name": settings.otel_service_name,
        "service.version": settings.version,
        "deployment.environment": settings.environment.value,
    })

    _tracer_provider = TracerProvider(resource=resource)

    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            insecure=True,
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(span_processor)
    except Exception as e:
        pass

    trace.set_tracer_provider(_tracer_provider)
    _tracer = trace.get_tracer(settings.otel_service_name)


def get_tracer():
    global _tracer
    if _tracer is None:
        setup_tracing()
    return _tracer


def get_tracer_provider():
    global _tracer_provider
    if _tracer_provider is None:
        setup_tracing()
    return _tracer_provider
