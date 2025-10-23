from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
import os


def redirect_request(method, url, headers, premium_proxy=False, dotenv_path=None, api_keyname="API_KEY", log_info=False, log_file=None):
    """
    Takes the url, headers, and method of an HTTP request and redirects it through ScrapingBee. Returns the response.
    Expects the ScrapingBee API key in a .env file; path can be configured but by default will search for ./.env.
    method: HTTP method
    url: url of a request, assumed to already be parsed
    headers: dict of HTTP headers
    premium_proxy: Optional argument, determines whether ScrapingBee will use its more expensive proxy
    dotenv_path: Optional argument, absolute or relative path to the .env file containing an API key to ScrapingBee.
    api_keyname: Optional argument, determines name of the API key's environment variable in the .env file.
    log_info: Optional argument, determines whether to provide additional log information.
    log_file: Optional argument, absolute or relative path to the output destination for logs. Default will be stderr.
    """
    load_dotenv(dotenv_path=dotenv_path)
    API_KEY = os.getenv(api_keyname)
    s_client = ScrapingBeeClient(API_KEY)
    prem_proxy = "true" if premium_proxy else "false"
    def log_message(message):
        if not log_info:
            return
        else:
            print(message,end="\n",file=log_file)
    try:
        accept_encoding = headers['Accept-Encoding']
    except KeyError:
        accept_encoding = None
    log_message(f"Redirecting: {method} {url}.")
    log_message(f"Headers: \n{headers}")
    scraped_response = s_client.request(method=method,
                                        url=url,
                                        params={
                                        'render_js': 'false',
                                        'return_page_source': 'true',
                                        'premium_proxy': prem_proxy,
                                        'forward_headers': 'true'
                                        },
                                        headers={'Accept-Encoding': accept_encoding} if accept_encoding else {},
                                        )
    log_message(f"Received {scraped_response.status_code}\n\nHeaders:\n{scraped_response.headers}\n\nContent:\n{scraped_response.content}")
    if not accept_encoding:
        scraped_response.headers['Content-Encoding'] = 'identity'

    return scraped_response
