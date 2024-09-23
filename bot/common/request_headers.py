import configparser
import logging

class RequestConfig:

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read('request.ini')

    def get_token(self) -> str:
        try:
            return self.config['request']['TOKEN']
        except KeyError as key_err:
            logging.log(logging.ERROR, f'{key_err}')

    def get_base_url(self) -> str:
        try:
            return self.config['request']['URL']
        except KeyError as key_err:
            logging.log(logging.ERROR, f'{key_err}')

    def get_request_headers(self) -> dict[str, str]:
        HEADERS = {
            'Authorization': f'Token {self.get_token()}',
            'Content-Type': 'application/json',
        }
        return HEADERS