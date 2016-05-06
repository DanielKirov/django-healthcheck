import json
from os import environ

from django.http import HttpResponse
from django.conf import settings
from django.db import connections
from django.contrib.sites.models import Site

import newrelic.agent


# FIXME:
# This is a copy paste job until the healthcheck app gets updated into it's own package
# The app will have to be scoped out, code-reviewed and live in it's own repository

def healthcheckview(request):

    # Before we do anything, make sure that NewRelic will treat this
    # as a background task.
    newrelic.agent.set_background_task()

    statuses = {}
    status_code = 200

    if settings.HEALTHCHECK_DATABASE:
        try:
            conn = connections['default']
            conn.cursor()
            statuses['Database'] = 'OK'
        except Exception:
            status_code = 500
            statuses['Database'] = 'NOT OK'

    if settings.HEALTHCHECK_ELASTICSEARCH:
        from elasticsearch import Elasticsearch
        es = Elasticsearch()
        if es.ping():
            statuses['ElasticSearch'] = 'OK'
        else:
            status_code = 500
            statuses['ElasticSearch'] = 'NOT OK'

    if settings.HEALTHCHECK_REDIS:
        import redis
        try:
            rs = redis.Redis(**_get_redis_info())
            response = rs.client_list()
            statuses['Redis'] = 'OK'
        except redis.ConnectionError:
            status_code = 500
            statuses['Redis'] = 'NOT OK'

    if settings.HEALTHCHECK_HOMEPAGE:
        import requests
        current_domain = Site.objects.get_current().domain
        try:
            response = requests.get("http://" + current_domain)
            statuses['Home page status'] = response.status_code
            if response.status_code != 200:
                status_code = 500
        except Exception:
            status_code = 500
            statuses['Home page status'] = 'NOT OK'

    # Add the status code to the payload
    payload = {
        'status_code': status_code,
    }

    # Add all other data to the payload
    payload.update(statuses)

    # Return a response
    return HttpResponse(
        json.dumps(payload),
        status=status_code,
        content_type="application/json"
    )


def _get_redis_info():
    'Fetches the REDIS URL from the ENV and splits into components'

    redis_url_str = environ.get(
        'REDIS_LOCATION', 'localhost:6379:0'
    ).split(':')

    return {
        'host': redis_url_str[0],
        'port': redis_url_str[1],
        'db': redis_url_str[2],
    }
