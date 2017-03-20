import os
from . import base, staging, prod

settings = base.settings

if os.getenv('ENVIRONMENT') == 'staging':
    settings.update(staging.settings)


if os.getenv('ENVIRONMENT') == 'prod':
    settings.update(prod.settings)
