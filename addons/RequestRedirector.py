from scrapingbee import ScrapingBeeClient
import logging
from dotenv import load_dotenv
from mitmproxy import http
import os

class RequestRedirector:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('API_KEY')
        self.s_client = ScrapingBeeClient(self.API_KEY)
        self.premium_proxy_needed = 'false'
        self.logger = logging.getLogger('RequestRedirectorLog')
        self.logger.info("Logger set up!")

    def request(self, flow):
        request = flow.request
        self.logger.info(f"Redirecting request made to {request.url}")
        accept_encoding = None
        try:
            accept_encoding = request.headers['Accept-Encoding']
        except KeyError:
            accept_encoding = None

        scraped_response = self.s_client.request(method=request.method,
                                                 url=request.url,
                                                 params={
                                                     'render_js': 'false',
                                                     'return_page_source': 'true',
                                                     'premium_proxy': self.premium_proxy_needed,
                                                     'forward_headers':'true'
                                                 },
                                                 headers={'Accept-Encoding':accept_encoding} if accept_encoding else {},
                                                 )
        if 400 <= scraped_response.status_code < 500:
            self.premium_proxy_needed = 'true'

        #Issues?
        if not accept_encoding:
            scraped_response.headers['Content-Encoding'] = 'identity'

        flow.response = http.Response.make(
            status_code=scraped_response.status_code,
            content=scraped_response.content,
            headers=dict(scraped_response.headers)
            )

        self.logger.info(f"Response: {flow.response.status_code} \n{flow.response.headers}\n{flow.response.content}")

addons = [RequestRedirector()]
