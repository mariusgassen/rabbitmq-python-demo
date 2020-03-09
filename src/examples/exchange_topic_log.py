import time
from argparse import ArgumentParser
from threading import Thread

from log_subscribers import ConsoleLogSubscriber, FileLogSubscriber
from publisher import Publisher
from subscriber import Subscriber
from util import add_rabbitmq_args

if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    args = parser.parse_args()

    host = args.ip
    port = args.port
    username = args.username
    password = args.credentials
    exchange_name = 'topic_log'
    exchange_type = 'topic'

    publisher = Publisher(name='log_pub', host=host, port=port, username=username, password=password,
                          exchange_name=exchange_name, exchange_type=exchange_type, durable_exchange=False)
    all_c_subscriber = ConsoleLogSubscriber(name='all_console', host=host, port=port, username=username,
                                            password=password, exchange_name=exchange_name, exchange_type=exchange_type)
    kern_c_subscriber = ConsoleLogSubscriber(name='kern_console', host=host, port=port, username=username, password=password,
                                        exchange_name=exchange_name, exchange_type=exchange_type)
    critical_f_subscriber = FileLogSubscriber(name='critical_file', log_file='criticial_log.log', host=host, port=port, username=username,
                                     password=password,
                                     exchange_name=exchange_name, exchange_type=exchange_type)
    critical_or_kern_f_subscriber = FileLogSubscriber(name='critical_or_kern_file', log_file='criticial_or_kern_log.log', host=host, port=port, username=username,
                                     password=password,
                                     exchange_name=exchange_name, exchange_type=exchange_type)
    critical_and_kern_f_subscriber = FileLogSubscriber(name='critical_and_kern_file', log_file='criticial_and_kern_log.log', host=host, port=port, username=username,
                                     password=password,
                                     exchange_name=exchange_name, exchange_type=exchange_type)

    all_c_thread = Thread(target=all_c_subscriber.start_receive, args=(True, ['#']))
    kern_c_thread = Thread(target=kern_c_subscriber.start_receive, args=(True, ['kern.*']))
    critical_f_thread = Thread(target=critical_f_subscriber.start_receive, args=(True, ['*.critical']))
    critical_or_kern_f_thread = Thread(target=critical_or_kern_f_subscriber.start_receive, args=(True, ['kern.*', '*.critical']))
    critical_and_kern_f_thread = Thread(target=critical_and_kern_f_subscriber.start_receive, args=(True, ['kern.critical']))

    all_c_thread.start()
    kern_c_thread.start()
    critical_f_thread.start()
    critical_and_kern_f_thread.start()
    critical_or_kern_f_thread.start()

    # give the sub thread a second to run
    time.sleep(1)

    publisher.publish(message='Some rather unimportant message', routing_key='anonymous.info')
    publisher.publish(message='Some kernel info', routing_key='kern.info')
    publisher.publish(message='Some kernel error', routing_key='kern.error')
    publisher.publish(message='Some critical kernel error', routing_key='kern.critical')
    publisher.publish(message='Some ui error', routing_key='ui.error')
    publisher.publish(message='You should look at this!', routing_key='ui.critical')