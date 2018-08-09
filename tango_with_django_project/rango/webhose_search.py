import json
import urllib.parse
import urllib.request


def read_webhose_key():
    # Read the webhose API key from a file called 'search.key'.
    # Returns either None (no key found) or a Str representing the key.
    webhose_api_key = None

    try:
        with open('search.key','r') as f:
            webhose_api_key = f.readline().strip()

    except:
        raise IOError('search.key file not found')

    return webhose_api_key


def run_query(search_terms, size=10):
    # Given a string containing a query (search terms), and a number
    # of results to return (10), returns a list of results from
    # the webhose API (with title, link and summary)
    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('Webhose key not found')

    # The root url
    root_url = 'http://webhose.io/filterWebContent'

    # format the query string to escape special characters
    query_string = urllib.parse.quote(search_terms)

    # Use string formatting to construct the complete API URL.
    # search_url is a string split over multiple lines.
    search_url = ('{root_url}?token={key}&format=json'
                  '&sort=relevancy&q={query}').format(
                    root_url=root_url,
                    key=webhose_api_key,
                    query=query_string,
                    size=size)
    print(search_url)
    results = []

    try:
        print('im here')
        # Connect to the webhose API and convert the response
        # to a python dictionary
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)

        # loop through the posts and append each to the results list
        # as a dictionary. (only take the first 200 charachters for the summary)
        for post in json_response['posts']:
            results.append({'title': post['title'],
                            'link': post['url'],
                            'summary': post['text'][:200]})

    except:
        print('Error when querying the webhose API')

    return results