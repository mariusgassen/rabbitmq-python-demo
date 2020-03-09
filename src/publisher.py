import logging

from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from pika.channel import Channel
from pika.exceptions import ChannelWrongStateError, ConnectionWrongStateError
from pika.spec import Exchange

logger = logging.getLogger('rabbitmq-publisher')
logging.basicConfig()
logger.setLevel(level=logging.DEBUG)


class Publisher:
    def __init__(self, name='X',
                 host='localhost',
                 port=5672,
                 username='admin',
                 password='pass',
                 exchange_name='ex',
                 exchange_type='fanout',
                 durable_exchange=False):
        self.name = name
        credentials = PlainCredentials(username=username, password=password)
        params = ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = BlockingConnection(parameters=params)
        self.channel: Channel = self.connection.channel()
        self.exchange_name = exchange_name
        self.exchange: Exchange = self.channel.exchange_declare(exchange=exchange_name,
                                                                exchange_type=exchange_type,
                                                                durable=durable_exchange)

    def publish(self, message: str, routing_key: str = '', exchange: str = None):
        if not exchange:
            exchange = self.exchange_name
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        logger.info(f'[{self.name}] Published message "{message}" to exchange "{exchange}" with key "{routing_key}"')

    def close_connection(self):
        try:
            self.channel.close()
            self.connection.close()
        except ChannelWrongStateError as e:
            logger.error(f'Error closing channel: {e}')
        except ConnectionWrongStateError as e:
            logger.error(f'Error closing connection: {e}')
