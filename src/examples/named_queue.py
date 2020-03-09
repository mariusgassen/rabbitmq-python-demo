from argparse import ArgumentParser
from threading import Thread
from sender import Sender
from receiver import PrintReceiver
from util import add_rabbitmq_args

if __name__ == '__main__':
    parser = ArgumentParser()
    add_rabbitmq_args(parser)
    parser.add_argument('-m', '--messages', type=str, nargs='*', default=[])
    parser.add_argument('-ack', '--auto_ack', type=bool, default=True)
    args = parser.parse_args()

    # Single Receiver and Sender
    receiver = PrintReceiver(name='1',
                             host=args.ip,
                             port=args.port,
                             username=args.username,
                             password=args.credentials,
                             delay=0.0)
    sender = Sender(host=args.ip, port=args.port, username=args.username, password=args.credentials)
    receiver_thread = Thread(target=receiver.start_receive, args=(args.queue, args.auto_ack))
    sender_thread = Thread(target=sender.send_multiple, args=(args.messages, 1.0, args.queue, args.exchange))

    # receiver will not terminate
    receiver_thread.start()
    sender_thread.start()
    sender_thread.join()
