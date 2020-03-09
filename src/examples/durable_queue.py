from argparse import ArgumentParser
from threading import Thread
from sender import Sender
from receiver import PrintReceiver
from util import add_rabbitmq_args

if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    parser.add_argument('-m', '--messages', type=str, nargs='*', default=['Message 1', 'Message 2'])

    args = parser.parse_args()

    non_durable_queue = 'non_durable_queue'
    durable_queue = 'durable_queue'
    sender = Sender(host=args.ip, port=args.port, username=args.username, password=args.credentials)
    # Non durable queue and message will be lost
    sender.send(queue=non_durable_queue, message='Wont see this one after restart', durable_queue=False, durable=False)
    # Durable messages on durable queue will success
    sender.send_multiple(queue=durable_queue, messages=args.messages, durable_queue=True, durable=True)
    # Non durable message on durable queue will be gona
    sender.send(queue=durable_queue, message='Wont see this one after restart either although on durable queue', durable_queue=True, durable=False)
