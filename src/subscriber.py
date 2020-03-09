import logging
from abc import ABC, abstractmethod
from typing import List
from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from pika.channel import Channel
from pika.spec import Exchange
from datetime import datetime

logger = logging.getLogger('rabbitmq-subscriber')
logging.basicConfig()
logger.setLevel(level=logging.DEBUG)


class Subscriber(ABC):
    def __init__(self,
                 name='s',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass',
                 exchange_name='ex',
                 exchange_type='direct'):
        self.name = name
        credentials = PlainCredentials(username=username, password=password)
        params = ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = BlockingConnection(parameters=params)
        self.channel: Channel = self.connection.channel()
        self.exchange_name = exchange_name
        self.exchange: Exchange = self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)
        self.queue = None

    @staticmethod
    def _decode_message(message, encoding='utf-8'):
        return message.decode(encoding)

    def start_receive(self, exclusive=False, routing_keys: List[str]=None):
        declaration = self.channel.queue_declare(queue='', exclusive=exclusive)
        self.queue = declaration.method.queue
        if routing_keys:
            for routing_key in routing_keys:
                self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue, routing_key=routing_key)
        else:
            self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue)
        logger.info(f'[{self.name}] Subscribed to message on exchange "{self.exchange_name}".')
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    @abstractmethod
    def callback(self, ch, method, properties, body):
        pass


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
                 log_file='file_log.log'):
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