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
    exchange_name = 'direct_logs'
    exchange_type = 'direct'

    sev_error = 'error'
    sev_warn = 'warn'
    sev_info = 'info'

    publisher = Publisher(name='log_pub', host=host, port=port, username=username, password=password,
                          exchange_name=exchange_name, exchange_type=exchange_type, durable_exchange=False)
    c_subscriber = ConsoleLogSubscriber(name='console', host=host, port=port, username=username, password=password,
                                        exchange_name=exchange_name, exchange_type=exchange_type)
    f_subscriber = FileLogSubscriber(name='file', log_file='direct_log.log', host=host, port=port, username=username, password=password,
                                     exchange_name=exchange_name, exchange_type=exchange_type)

    # log everything to file but only errors to console
    c_thread = Thread(target=c_subscriber.start_receive, args=(True, [sev_error]))
    f_thread = Thread(target=f_subscriber.start_receive, args=(True, [sev_warn, sev_error]))

    f_thread.start()
    c_thread.start()

    # give the sub thread a second to run
    time.sleep(1)

    publisher.publish(message='VERY IMPORTANT', routing_key=sev_error)
    publisher.publish(message='This one is discarded', routing_key=sev_info)
    publisher.publish(message='This will only appear in the file log', routing_key=sev_warn)
    publisher.publish(message='SUPER IMPORANT CRASH REPORT', routing_key=sev_error)
