import logging
import sys

# algorithms
from app import macd
from app import bollinger

# market
from app import market as mkt


# configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initiated")

MACD_TRADES_EVENT = 'MACD_TRADES'
BOLLINGER_TRADES_EVENT = 'BOLLINGER_TRADES'


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
    if event_type == BOLLINGER_TRADES_EVENT:
        logger.info('bollinger trades event received: %s', str(event))
        return bollinger_trades_handler(exchange, market, event)


def macd_trades_handler(exchange, market, event_params):
    market_order = mkt.predict_market_trade(
        macd.predict_behavior, logger, exchange, market, **event_params)
    return market_order.place_trade(exchange)


def bollinger_trades_handler(exchange, market, event_params):
    open_orders = mkt.get_open_limit_orders_for_market(
        logger, exchange, market)
    for order in open_orders:
        logger.info('cancel: %s', order.order_id)
        order.cancel(exchange)
    if not open_orders:
        logger.info('no open orders to cancel')
    upper_limit_order, lower_limit_order = mkt.predict_limit_bounds_trade(
        bollinger.predict_behavior, logger, exchange, market, **event_params)
    if upper_limit_order:
        logger.info('predicted order: %s %s %s %s', upper_limit_order.market, upper_limit_order.side,
                    upper_limit_order.price, upper_limit_order.trading_amount)
        upper_limit_order.place_trade(exchange)
    else:
        logger.info("no sell order possible")
    if lower_limit_order:
        logger.info('predicted order: %s %s %s %s', lower_limit_order.market, lower_limit_order.side,
                    lower_limit_order.price, lower_limit_order.trading_amount)
        lower_limit_order.place_trade(exchange)
    else:
        logger.info("no buy order possible")
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    event_handler({
        'type': sys.argv[1],
        'exchange': sys.argv[2],
        'market': sys.argv[3],
    }, None)
