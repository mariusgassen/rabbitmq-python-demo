from argparse import ArgumentParser
from threading import Thread
from sender import Sender
from receiver import DotReceiver
from util import add_rabbitmq_args

if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    parser.add_argument('-m', '--messages', type=str, nargs='*',
                        default=['First', 'Second....', 'Third......', 'Fourth....', 'Fifth...', 'Sixth....'])
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
                            password=args.credentials,
                            die_on_message=1)

    receiver3 = DotReceiver(name='3',
                            host=args.ip,
                            port=args.port,
                            username=args.username,
                            password=args.credentials,
                            die_on_message=1)

    sender = Sender(host=args.ip, port=args.port, username=args.username, password=args.credentials)
    # auto_ack is False!
    # Always processes
    receiver_thread_1 = Thread(target=receiver.start_receive, args=(args.queue, False))
    # Dies on message 1 but does not auto-ACK - message will be resent
    receiver_thread_2 = Thread(target=receiver2.start_receive, args=(args.queue, False))
    # Dies on message 1 one but auto-ACKs - message is lost
    receiver_thread_3 = Thread(target=receiver3.start_receive, args=(args.queue, True))
    sender_thread = Thread(target=sender.send_multiple, args=(args.messages, 0.0, args.queue, args.exchange))

    # notice the round robin, if tasks have different sizes periodically (e.g. each 3rd is long)
    # other workers will be idle
    receiver_thread_1.start()
    receiver_thread_2.start()
    receiver_thread_3.start()
    sender_thread.start()
    sender_thread.join()
