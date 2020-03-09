import logging
import os
from datetime import datetime

from subscriber import Subscriber

logger = logging.getLogger('log-subscriber')
logging.basicConfig()
logger.setLevel(level=logging.DEBUG)


class ConsoleLogSubscriber(Subscriber):

    def callback(self, ch, method, properties, body):
        message = self._decode_message(message=body)
        timestamp = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
        logger.debug(f'[{self.name}] Received log message {message}')
        print(f'[{self.name}] {timestamp} {message}')


class FileLogSubscriber(Subscriber):
    def __init__(self, name='file_logger',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass',
                 exchange_name='ex',
                 exchange_type='direct',
                 log_file='rabbit_mq_sub.log'):
        self.log_file = log_file
        Subscriber.__init__(self, name=name,
                            host=host,
                            port=port,
                            username=username,
                            password=password,
                            exchange_name=exchange_name,
                            exchange_type=exchange_type)

    def _log_to_file(self, message):
        with open(self.log_file, 'a') as log:
            timestamp = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
            log.write(f'{timestamp} {message}\n')
            log.close()

    def callback(self, ch, method, properties, body):
        message = self._decode_message(message=body)
        logger.debug(f'[{self.name}] Received log message {message}')
        self._log_to_file(message)