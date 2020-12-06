import requests
import logging
import json

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

headers = {
    'accept': 'application/json',
    'content-type': 'application/json'
}


def handler_get_quote(event, context):
    LOG.info("EVENT: " + json.dumps(event))
    language = 'en'
    try:
        language = event["queryStringParameters"]["language"] or language
    except:
        pass

    r = requests.get(
        'https://quotes.rest/qod?language={}'.format(language), headers=headers)

    return {
        'statusCode': r.status_code,
        'body': r.text
    }


def handler_get_languages(event, context):
    LOG.info("EVENT: " + json.dumps(event))
    r = requests.get('https://quotes.rest/qod/languages', headers=headers)

    return {
        'statusCode': r.status_code,
        'body': r.text
    }
