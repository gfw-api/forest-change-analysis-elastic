import logging
import os

import RWAPIMicroservicePython
from flask import Flask

from gladanalysis.config import settings
from gladanalysis.routes.api.v2 import endpoints

# Logging
logging.basicConfig(
    level=settings.get('logging', {}).get('level'),
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y%m%d-%H:%M%p',
)


def create_application():
    # Flask
    application = Flask(__name__)

    # Config
    application.config.from_object(settings)

    # Routing
    application.register_blueprint(endpoints, url_prefix='/api/v2/ms')

    RWAPIMicroservicePython.register(
        app=application,
        gateway_url=os.getenv('GATEWAY_URL'),
        token=os.getenv('MICROSERVICE_TOKEN'),
        aws_cloud_watch_logging_enabled=(os.getenv('AWS_CLOUD_WATCH_LOGGING_ENABLED', 'True').lower() == 'true'),
        aws_cloud_watch_log_stream_name=settings.get('service', {}).get('name'),
        aws_region=os.getenv('AWS_REGION'),
        require_api_key=(os.getenv('REQUIRE_API_KEY', 'False').lower() == 'true')
    )

    return application
