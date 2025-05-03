import re
import threading
import time
import connexion
from flask import request
from prometheus_client import start_http_server, Counter, Gauge
from sqlalchemy import func
from swagger_server import encoder
from swagger_server.database import db
from swagger_server.logger import logger

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)

# Создание ресурса с именем сервиса
resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "python_server"
})

# Создание провайдера трейсеров с ресурсом
tracer_provider = TracerProvider(resource=resource)

# Создание экспортера
otlp_exporter = OTLPSpanExporter(endpoint="http://tempo:4317", insecure=True)

# Создание процессора спанов и добавление его в провайдер
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Установка провайдера трейсеров
trace.set_tracer_provider(tracer_provider)

# Получение трейсеров
tracer = trace.get_tracer(__name__)

from swagger_server.models import Product


def update_endpoint(endpoint, method):
    match = re.match(r"^(.*)/(\d+)$", endpoint)
    if match:
        return match.group(1) + '/' + method
    else:
        if method == 'GET':
            return endpoint + '/GET_ALL'
        return endpoint + '/' + method


# Создаем метрику запроса с метками для пути запроса и метода
REQUEST_COUNT = Counter('http_requests_total',
                        'Total HTTP Requests',
                        ['endpoint', 'method'])
product_creation_counter = Gauge('created_products',
                                 'Total figures count in the database')


def track_requests(app):
    @app.before_request
    def before_request():
        span_name = f"{request.method} {request.path}"
        span = tracer.start_span(span_name)
        request._otel_span = span

        endpoint = request.path
        method = request.method
        if '/product' in endpoint:
            endpoint = update_endpoint(endpoint, method)
        REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc()

    @app.after_request
    def after_request(response):
        span = getattr(request, '_otel_span', None)
        if span:
            span.end()
        return response


def update_system_metrics(app):
    while True:
        with app.app_context():
            # Создаем трейс с тремя спанами
            with tracer.start_as_current_span("system_metrics_update") as parent_span:
                # Первый спан - получение количества продуктов
                with tracer.start_as_current_span("get_product_count"):
                    count = db.session.query(func.count(Product.id)).scalar()

                # Второй спан - установка метрики
                with tracer.start_as_current_span("set_metric_value"):
                    product_creation_counter.set(count)

                # Третий спан - пауза
                with tracer.start_as_current_span("sleep_interval"):
                    time.sleep(1)


def main():
    start_http_server(8000)
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml',
                arguments={'title': 'Складское управление API'},
                pythonic_params=True)

    # Регистрируем middleware для отслеживания запросов
    track_requests(app.app)

    # Конфигурация SQLAlchemy для SQLite
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app.app)

    logger.info("Сервер запущеен")

    with app.app.app_context():
        db.create_all()

    threading.Thread(target=update_system_metrics,
                     args=(app.app,),
                     daemon=True).start()
    app.run(port=5000)


if __name__ == '__main__':
    main()
