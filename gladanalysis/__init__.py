import logging
import os

import RWAPIMicroservicePython
from flask import Flask

from gladanalysis.config import settings
from gladanalysis.routes.api.v2 import endpoints
from gladanalysis.utils.files import load_config_json

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

    # CT
    info = load_config_json('register')
    swagger = load_config_json('swagger')
    RWAPIMicroservicePython.register(
        app=application,
        name='ms',
        info=info,
        swagger=swagger,
        mode=RWAPIMicroservicePython.AUTOREGISTER_MODE if os.getenv('CT_REGISTER_MODE') and os.getenv(
            'CT_REGISTER_MODE') == 'auto' else RWAPIMicroservicePython.NORMAL_MODE,
        ct_url=os.getenv('CT_URL'),
        url=os.getenv('LOCAL_URL'),
        token=os.getenv('CT_TOKEN'),
        api_version=os.getenv('API_VERSION')
    )

    return application
