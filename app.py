import logging
import macd
import sys
import market as mkt

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initiated")

MAKE_TRADES_EVENT = 'MAKE_TRADES'


class MakeTradesEvent:
    def __init__(self, exchange):
        self.exchange = exchange


def event_handler(event, context):
    logger.info('event received: %s', str(event))
    if event['type'] == MAKE_TRADES_EVENT:
        return make_trades_handler(event)


def make_trades_handler(event):
    logger.info('make trades event received: %s', str(event))

    event = MakeTradesEvent(event['exchange'])
    exchange = mkt.get_exchange(event.exchange)
    logger.info('exchange configured')
    return macd.find_and_act_on_markets(exchange, logger)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    make_trades_handler({'exchange': sys.argv[1]})

