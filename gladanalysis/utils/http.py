import os
import json
from requests import Request, Session


CT_URL = os.getenv('CT_URL')
CT_TOKEN = os.getenv('CT_TOKEN')


def request_to_microservice(config):
    try:
        session = Session()
        request = Request(
                method=config.get('method'),
                url=CT_URL + config.get('uri'),
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Bearer '+CT_TOKEN
                },
                data=json.dumps(config.get('body'))
            )
        prepped = session.prepare_request(request)
    
        response = session.send(prepped)
    except Exception as error:
       raise error

    return response.json()
