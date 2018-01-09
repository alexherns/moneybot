import os
import ccxt
import math

_api_key_addresss = "_API_KEY"
_api_secret_address = "_API_SECRET"


SELL_FRACTION = 1.0
BUY_FRACTION = 0.45


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
        if self.side == SIDE_HODL:
            return None
        if self.side == SIDE_BUY:
            return exchange.create_limit_buy_order(self.market, self.trading_amount, self.price)
        else:
            return exchange.create_limit_sell_order(self.market, self.trading_amount, self.price)


class Market_Trade:
    def __init__(self, market, side, trading_amount):
        if side not in (SIDE_HODL, SIDE_BUY, SIDE_SELL):
            raise Exception('Unknown side for execution')
        self.market = market
        self.side = side
        self.trading_amount = trading_amount

    def place_trade(self, exchange):
        if self.side == SIDE_HODL:
            return None
        if self.side == SIDE_BUY:
            return exchange.create_market_buy_order(self.market, self.trading_amount)
        else:
            return exchange.create_market_sell_order(self.market, self.trading_amount)


def fetch_limits(exchange, market):
    mkt_limits = exchange.market(market)['limits']
    return Market_Limit(
        min_price=mkt_limits['price']['min'],
        max_price=mkt_limits['price']['max'],
        min_qty=mkt_limits['amount']['min'],
        max_qty=mkt_limits['amount']['max']
    )


def get_exchange(exchange=EXCHANGE_BINANCE):
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
    amount = get_trading_amount(logger, limits, market, side, balance, ticker)
    logger.info('amount predicted %s', str(amount))
    return Market_Trade(market, side, amount)


def get_trading_amount(logger, limits, market, side, balance, ticker):
    if side == SIDE_HODL:
        return None
    elif side not in (SIDE_BUY, SIDE_SELL):
        raise Exception('Unknown side for execution')
    if side == SIDE_BUY:
        purchasing_currency = market.split('/')[1]
        purchasing_funds = balance[purchasing_currency] * BUY_FRACTION
        trade_amount = purchasing_funds * ticker['ask']
        logger.info('buying %s with %s at %s with %s gives %s total', market.split(
            '/')[0], purchasing_currency, ticker['ask'], purchasing_funds, trade_amount)
    elif side == SIDE_SELL:
        sell_currency = market.split('/')[0]
        trade_amount = balance[sell_currency] * SELL_FRACTION
        logger.info('selling %s for %s gives %s total',
                    sell_currency, market.split('/')[0], trade_amount)
    trade_amount = math.floor(trade_amount / limits.price_filter.tick_size) * \
        limits.price_filter.tick_size
    logger.info('funds available results in %s sale', trade_amount)
    if trade_amount < limits.lot_size.min_qty:
        return None
    return trade_amount
