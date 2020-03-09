import time
from argparse import ArgumentParser
from threading import Thread

from log_subscribers import ConsoleLogSubscriber, FileLogSubscriber
from publisher import Publisher
from util import add_rabbitmq_args


if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    args = parser.parse_args()

    host = args.ip
    port = args.port
    username = args.username
    password = args.credentials
    exchange_name = 'logs'
    exchange_type = 'fanout'
    publisher = Publisher(name='log_pub', host=host, port=port, username=username, password=password,
                          exchange_name=exchange_name, exchange_type=exchange_type, durable_exchange=False)

    publisher.publish(message='Lost log message')

    c_subscriber = ConsoleLogSubscriber(name='console', host=host, port=port, username=username, password=password,
                                        exchange_name=exchange_name, exchange_type=exchange_type)
    f_subscriber = FileLogSubscriber(name='file', host=host, port=port, username=username, password=password,
                                     exchange_name=exchange_name, exchange_type=exchange_type)

    c_thread = Thread(target=c_subscriber.start_receive, args=(True,))
    f_thread = Thread(target=f_subscriber.start_receive, args=(True,))

    f_thread.start()

    # give the sub thread a second to run
    time.sleep(1)

    publisher.publish(message='Will only find this in the file log')

    c_thread.start()
    # give the sub thread a second to run
    time.sleep(1)

    publisher.publish(message='Will find this in both logs')
