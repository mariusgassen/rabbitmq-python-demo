import logging
import time
from argparse import ArgumentParser
from abc import ABC, abstractmethod
from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from pika.channel import Channel
from util import add_rabbitmq_args

logger = logging.getLogger('rabbitmq-receiver')
logging.basicConfig()
logger.setLevel(level=logging.DEBUG)


class Receiver(ABC):

    def __init__(self,
                 name='receiver',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass'):
        self.name = name
        credentials = PlainCredentials(username=username, password=password)
        params = ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = BlockingConnection(parameters=params)
        self.channel: Channel = self.connection.channel()
        self.message_counter = 0

    @staticmethod
    def _decode_message(message, encoding='utf-8'):
        return message.decode(encoding)

    def start_receive(self, queue: str = 'hello', auto_ack=True, prefetch_count=None):
        logger.info(f'[{self.name}] Waiting for messages on queue "{queue}".')
        self.channel.queue_declare(queue=queue)
        if prefetch_count and prefetch_count > 0:
            self.channel.basic_qos(prefetch_count=prefetch_count)
        if auto_ack:
            self.channel.basic_consume(queue=queue, on_message_callback=self.callback, auto_ack=auto_ack)
        else:
            self.channel.basic_consume(queue=queue, on_message_callback=self.callback_ack, auto_ack=auto_ack)
        self.channel.start_consuming()

    def kill(self):
        self.connection.close()

    def _process_message(self, message):
        pass

    @abstractmethod
    def callback(self, ch, method, properties, body):
        pass

    @abstractmethod
    def callback_ack(self, ch, method, properties, body):
        pass


class PrintReceiver(Receiver):

    def __init__(self,
                 name='receiver',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass',
                 delay: float = 0.0):
        self.processing_delay = delay
        Receiver.__init__(self,
                          name=name,
                          host=host,
                          port=port,
                          username=username,
                          password=password)

    def _process_message(self, body):
        self.message_counter += 1
        logger.info(f'[{self.name}] Received message {self.message_counter}: "{self._decode_message(body)}')
        logger.info(f'[{self.name}] Processing...')
        time.sleep(self.processing_delay)

    def callback(self, ch, method, properties, body):
        self._process_message(body)

    def callback_ack(self, ch, method, properties, body):
        self._process_message(body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f'[{self.name}] Acknowledged tag {method.delivery_tag}')


class DotReceiver(Receiver):
    def __init__(self,
                 name='receiver',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass',
                 prefetch: int = None,
                 die_on_message: int = None):
        self.die_on_message = die_on_message
        Receiver.__init__(self,
                          name=name,
                          host=host,
                          port=port,
                          username=username,
                          password=password)

    @staticmethod
    def _get_processing_time(message):
        return float(len([c for c in message if c == '.']))

    def _process_message(self, body):
        self.message_counter += 1
        message = self._decode_message(body)
        logger.info(f'[{self.name}] Received message {self.message_counter}: "{message}"')
        delay = self._get_processing_time(message)
        logger.info(f'[{self.name}] Processing for {delay} seconds...')
        time.sleep(delay)

    def callback(self, ch, method, properties, body):
        self._process_message(body)
        if self.die_on_message and self.die_on_message >= self.message_counter:
            logger.error(
                f'[{self.name}] Error occured processing message "{self._decode_message(body)}". Message is lost.')
            self.kill()

    def callback_ack(self, ch, method, properties, body):
        self._process_message(body)
        if self.die_on_message and self.die_on_message >= self.message_counter:
            logger.error(f'[{self.name}] Error occured processing message "{self._decode_message(body)}". No ACK sent.')
            self.kill()
            return
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f'[{self.name}] Acknowledged tag {method.delivery_tag}')


if __name__ == '__main__':
    if __name__ == '__main__':
        parser = ArgumentParser()
        add_rabbitmq_args(parser)
        parser.add_argument('-ack', '--auto_ack', type=bool, default=True)
        args = parser.parse_args()

        receiver = PrintReceiver(host=args.ip, port=args.port, username=args.username, password=args.credentials)
        receiver.start_receive(queue=args.queue, auto_ack=args.auto_ack)
