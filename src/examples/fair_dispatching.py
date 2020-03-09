from argparse import ArgumentParser
from threading import Thread
from sender import Sender
from receiver import DotReceiver
from util import add_rabbitmq_args

import os
from datetime import datetime


if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    parser.add_argument('-m', '--messages', type=str, nargs='*',
                        default=['Hello.', 'Hello........', 'Hello.', 'Hello........', 'Hello.', 'Hello........'])
    args = parser.parse_args()

    # Multiple receivers with different delays and Sender
    receiver = DotReceiver(name='1',
                           host=args.ip,
                           port=args.port,
                           username=args.username,
                           password=args.credentials)

    receiver2 = DotReceiver(name='2',
                            host=args.ip,
                            port=args.port,
                            username=args.username,
                            password=args.credentials)

    sender = Sender(host=args.ip, port=args.port, username=args.username, password=args.credentials)
    # Use prefetch count, will skip the receiver if it is still busy. Not only receiver 2 will get the long tasks
    receiver_thread_1 = Thread(target=receiver.start_receive, args=(args.queue, False, 1))
    receiver_thread_2 = Thread(target=receiver2.start_receive, args=(args.queue, False, 1))
    sender_thread = Thread(target=sender.send_multiple, args=(args.messages, 0.0, args.queue, args.exchange))

    receiver_thread_1.start()
    receiver_thread_2.start()
    sender_thread.start()
    sender_thread.join()
