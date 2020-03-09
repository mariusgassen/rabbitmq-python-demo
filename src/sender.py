import time
from threading import Thread
from typing import List

from pika import PlainCredentials, ConnectionParameters, BlockingConnection, BasicProperties
from pika.channel import Channel
from pika.exceptions import ChannelWrongStateError, ConnectionWrongStateError
from argparse import ArgumentParser
import logging
from util import add_rabbitmq_args

logger = logging.getLogger('rabbitmq-sender')
logging.basicConfig()
logger.setLevel(level=logging.DEBUG)


class Sender:
    def __init__(self, name='X', host='localhost', port=5672, username='admin', password='pass'):
        self.name = name
        credentials = PlainCredentials(username=username, password=password)
        params = ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = BlockingConnection(parameters=params)
        self.channel: Channel = self.connection.channel()

    def send(self, message: str, queue: str = 'hello', exchange='', durable_queue=False, durable=False):
        try:
            self.channel.queue_declare(queue=queue, durable=durable_queue)
            delivery_mode = 2 if durable else 1
            message_properties = BasicProperties(delivery_mode=delivery_mode)
            self.channel.basic_publish(exchange=exchange,
                                       routing_key=queue,
                                       body=message,
                                       properties=message_properties
                                       )
            logger.info(f'[{self.name}] Sent "{message}"')
        except ChannelWrongStateError as e:
            logger.error(f'[{self.name}] Error sending message on channel: {e}')

    def send_multiple(self, messages: List[str], delay: float = 0, queue: str = 'hello', exchange='',
                      durable_queue=False, durable=False):
        for message in messages:
            time.sleep(delay)
            self.send(message=message, queue=queue, exchange=exchange, durable_queue=durable_queue, durable=durable)

    def close_connection(self):
        try:
            self.channel.close()
            self.connection.close()
        except ChannelWrongStateError as e:
            logger.error(f'Error closing channel: {e}')
        except ConnectionWrongStateError as e:
            logger.error(f'Error closing connection: {e}')


if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    parser.add_argument('-m', '--messages', type=str, nargs='*', default=[])
    args = parser.parse_args()

    sender = Sender(host=args.ip, port=args.port, username=args.username, password=args.credentials)
    sender.send_multiple(args.messages, queue=args.queue, exchange=args.exchange, delay=1.0)
