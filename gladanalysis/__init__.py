import os
import json
import logging

from flask import Flask
from gladanalysis.config import settings
from gladanalysis.routes.api.v1 import endpoints
from gladanalysis.utils.files import load_config_json
import CTRegisterMicroserviceFlask

# Logging
logging.basicConfig(
    level = settings.get('logging', {}).get('level'),
    format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt = '%Y%m%d-%H:%M%p',
)


def create_application():
    # Flask
    application = Flask(__name__)

    # Config
    application.config.from_object(settings)

    # Routing
    application.register_blueprint(endpoints, url_prefix='/api/v1/ms')

    # CT
    info = load_config_json('register')
    swagger = load_config_json('swagger')
    CTRegisterMicroserviceFlask.register(
        app = application,
        name = 'ms',
        info = info,
        swagger = swagger,
        mode = CTRegisterMicroserviceFlask.AUTOREGISTER_MODE if os.getenv('ENVIRONMENT') == 'dev' else CTRegisterMicroserviceFlask.NORMAL_MODE,
        ct_url = os.getenv('CT_URL'),
        url = os.getenv('LOCAL_URL')
    )

    return application
