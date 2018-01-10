import os
import math
import ccxt
import common

_api_key_addresss = "_API_KEY"
_api_secret_address = "_API_SECRET"


MARKET_TRADE_SELL_FRACTION = 1.0
MARKET_TRADE_BUY_FRACTION = 0.45

LIMIT_BOUND_TRADE_FRACTION = 0.4


class Market:
    def __init__(self, exchange, market):
        self.exchange = exchange
        self.market = market
        self.limits = exchange.fetch_limits(market)


class Price_Filter:
    def __init__(self, min_price=0.0, max_price=0.0, tick_size=None):
        if tick_size is None:
            tick_size = min_price
        self.min_price = min_price
        self.max_price = max_price
        self.tick_size = tick_size


class Lot_Size:
    def __init__(self, min_qty=0.0, max_qty=0.0, step_size=None):
        if step_size is None:
            step_size = min_qty
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.step_size = step_size


class Market_Limit:
    def __init__(self, min_price=0.0, max_price=0.0, min_qty=0.0, max_qty=0.0, min_notional=None, tick_size=None, step_size=None):
        if min_notional is None:
            min_notional = min_price * min_qty
        self.price_filter = Price_Filter(
            min_price=min_price, max_price=max_price, tick_size=tick_size)
        self.lot_size = Lot_Size(
            min_qty=min_qty, max_qty=max_qty, step_size=step_size)
        self.min_notional = min_notional


class Limit_Trade:
    def __init__(self, market, side, trading_amount, price):
        self.market = market
        self.side = side
        self.trading_amount = trading_amount
        self.price = price

    def place_trade(self, exchange):
        if self.side == common.SIDE_HODL:
            return None
        if self.side == common.SIDE_BUY:
            return exchange.create_limit_buy_order(self.market, self.trading_amount, self.price)
        else:
            return exchange.create_limit_sell_order(self.market, self.trading_amount, self.price)


class Market_Trade:
    def __init__(self, market, side, trading_amount):
        if side not in (common.SIDE_HODL, common.SIDE_BUY, common.SIDE_SELL):
            raise Exception('Unknown side for execution')
        self.market = market
        self.side = side
        self.trading_amount = trading_amount

    def place_trade(self, exchange):
        if self.side == common.SIDE_HODL:
            return None
        if self.side == common.SIDE_BUY:
            return exchange.create_market_buy_order(self.market, self.trading_amount)
        else:
            return exchange.create_market_sell_order(self.market, self.trading_amount)


class Limit_Order:
    def __init__(self, order_id, market):
        self.order_id = order_id
        self.market = market

    def cancel(self, exchange):
        return exchange.cancel_order(self.order_id, self.market)


def fetch_limits(exchange, market):
    mkt_filters = exchange.market(market)['info']['filters']
    mkt_limits = exchange.market(market)['limits']
    return Market_Limit(
        min_price=mkt_limits['price']['min'],
        max_price=mkt_limits['price']['max'],
        min_qty=mkt_limits['amount']['min'],
        max_qty=mkt_limits['amount']['max'],
        min_notional=float([mkt_filter['minNotional'] for mkt_filter in mkt_filters if mkt_filter['filterType'] == 'MIN_NOTIONAL'][0]),
        tick_size=float([mkt_filter['tickSize'] for mkt_filter in mkt_filters if mkt_filter['filterType'] == 'PRICE_FILTER'][0]),
        step_size=float([mkt_filter['stepSize'] for mkt_filter in mkt_filters if mkt_filter['filterType'] == 'LOT_SIZE'][0])
    )


def get_exchange(exchange):
    api_key = os.environ[exchange.upper() + _api_key_addresss]
    api_secret = os.environ[exchange.upper() + _api_secret_address]
    exc = getattr(ccxt, exchange.lower())({
        'apiKey': api_key,
        'secret': api_secret,
    })
    exc.load_markets()
    return exc


def predict_market_trade(market_trade_algorithm, logger, exchange, market, **kwargs):
    logger.info('evaluating market %s for behavior', market)
    side = market_trade_algorithm(exchange, market, **kwargs)
    logger.info('behavior predicted %s', side)
    limits = fetch_limits(exchange, market)
    balance = exchange.fetch_free_balance()
    ticker = exchange.fetchTicker(market)
    amount = get_market_trading_amount(
        logger, limits, market, side, balance, ticker)
    logger.info('amount predicted %s', str(amount))
    return Market_Trade(market, side, amount)


def get_market_trading_amount(logger, limits, market, side, balance, ticker):
    if side == common.SIDE_HODL:
        return None
    elif side not in (common.SIDE_BUY, common.SIDE_SELL):
        raise Exception('Unknown side for execution')
    if side == common.SIDE_BUY:
        purchasing_currency = market.split('/')[1]
        purchasing_funds = balance[purchasing_currency] * \
            MARKET_TRADE_BUY_FRACTION
        trade_amount = purchasing_funds * ticker['ask']
        logger.info('buying %s with %s at %s with %s gives %s total', market.split(
            '/')[0], purchasing_currency, ticker['ask'], purchasing_funds, trade_amount)
    elif side == common.SIDE_SELL:
        sell_currency = market.split('/')[0]
        trade_amount = balance[sell_currency] * MARKET_TRADE_SELL_FRACTION
        logger.info('selling %s for %s gives %s total',
                    sell_currency, market.split('/')[0], trade_amount)
    trade_amount = get_rounded_trading_amount(
        trade_amount, limits.price_filter.tick_size, limits.lot_size.min_qty)
    logger.info('funds available results in %s sale', trade_amount)
    if trade_amount < limits.lot_size.min_qty:
        return None
    return trade_amount


def predict_limit_bounds_trade(limit_bounds_trade_algorithm, logger, exchange, market, **kwargs):
    logger.info('evaluating market %s for limit bounds trade', market)
    upper_bound, lower_bound = limit_bounds_trade_algorithm(
        exchange, market, **kwargs)
    logger.info('upper bound: %s, lower bound: %s', upper_bound, lower_bound)
    ticker = exchange.fetchTicker(market)
    sell_price = max(upper_bound, ticker['bid'])
    buy_price = min(lower_bound, ticker['ask'])
    logger.info('sell price: %s, buy price: %s', sell_price, buy_price)
    limits = fetch_limits(exchange, market)
    balance = exchange.fetch_free_balance()
    sell_amount, buy_amount = get_limit_bounds_trading_amount(
        limits, market, upper_bound, lower_bound, balance, ticker)
    logger.info('upper amount: %s, lower amount: %s', sell_amount, buy_amount)
    return (
        Limit_Trade(market, common.SIDE_SELL, sell_amount,
                    sell_price) if sell_amount else None,
        Limit_Trade(market, common.SIDE_BUY, buy_amount,
                    buy_price) if buy_amount else None
    )


def get_rounded_trading_amount(unrounded_amount, step_size, min_qty):
    rounded_amount = math.floor(unrounded_amount / step_size) * step_size
    if rounded_amount < min_qty:
        return None
    return rounded_amount


def get_limit_bounds_trading_amount(limits, market, upper_bound, lower_bound, balance, ticker):
    sell_currency, buy_currency = market.split('/')
    sell_funds = balance[sell_currency] * LIMIT_BOUND_TRADE_FRACTION
    buy_funds = balance[buy_currency] * LIMIT_BOUND_TRADE_FRACTION
    unrounded_sell_amount = sell_funds
    unrounded_buy_amount = buy_funds / ticker['ask']
    sell_amount = get_rounded_trading_amount(
        unrounded_sell_amount, limits.lot_size.step_size, limits.lot_size.min_qty)
    if sell_amount * upper_bound < limits.min_notional:
        sell_amount = None
    buy_amount = get_rounded_trading_amount(
        unrounded_buy_amount, limits.lot_size.step_size, limits.lot_size.min_qty)
    if buy_amount * lower_bound < limits.min_notional:
        buy_amount = None
    return sell_amount, buy_amount


# TODO: filter out non-limit orders! important so we can have a stop-limit below the limit orders
def get_open_limit_orders_for_market(logger, exchange, market):
    open_orders = exchange.fetch_open_orders(symbol=market)
    return [Limit_Order(open_order['id'], open_order['symbol']) for open_order in open_orders]
