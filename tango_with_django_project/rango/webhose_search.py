import json
import urllib.parse
import urllib.request


def read_webhose_key():
    webhose_api_key = None

    try:
        with open('search.key','r') as f:
            webhose_api_key = f.readline().strip()

    except:
        raise IOError('search.key file not found')

    return webhose_api_key