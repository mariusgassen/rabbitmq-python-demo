from argparse import ArgumentParser

def add_rabbitmq_args(parser: ArgumentParser):
    parser.add_argument('-i', '--ip', type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=5672)
    parser.add_argument('-ex', '--exchange', type=str, default='')
    parser.add_argument('-et', '--exchange_type', type=str, default='direct')
    parser.add_argument('-q', '--queue', type=str, default='hello')
    parser.add_argument('-u', '--username', type=str, default='admin')
    parser.add_argument('-c', '--credentials', type=str, default='pass')
    return parser