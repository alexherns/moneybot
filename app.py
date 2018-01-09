import logging
import macd
import sys
import market as mkt

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initiated")

MACD_TRADES_EVENT = 'MACD_TRADES'


def event_handler(event, context):
    logger.info('event received: %s', str(event))
    exchange = mkt.get_exchange(event['exchange'])
    logger.info('exchange configured')
    market = event['market']
    event_type = event['type']
    del event['exchange']
    del event['market']
    del event['type']
    if event_type == MACD_TRADES_EVENT:
        logger.info('macd trades event received: %s', str(event))
        return macd_trades_handler(exchange, market, event)


def macd_trades_handler(exchange, market, event_params):
    market_order = mkt.predict_market_trade(
        macd.predict_behavior, logger, exchange, market, **event_params)
    return market_order.place_trade(exchange)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    event_handler(
        {'type': sys.argv[1], 'exchange': sys.argv[2], 'market': sys.argv[3]}, None)
