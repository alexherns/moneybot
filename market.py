import os
import ccxt

_api_key_addresss = "_API_KEY"
_api_secret_address = "_API_SECRET"

EXCHANGE_BINANCE = 'BINANCE'

SIDE_HODL = "hodl"
SIDE_SELL = "sell"
SIDE_BUY = "buy"


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


def execute_market_trade(exchange, market, side, trading_amount):
    if side == SIDE_HODL:
        return None
    elif side not in (SIDE_BUY, SIDE_SELL):
        raise Exception('Unknown side for execution')
    if side == SIDE_BUY:
        return exchange.create_market_buy_order(market, trading_amount)
    else:
        return exchange.create_market_sell_order(market, trading_amount)


def execute_limit_trade(exchange, market, side, trading_amount, price):
    if side == SIDE_HODL:
        return None
    elif side not in (SIDE_BUY, SIDE_SELL):
        raise Exception('Unknown side for execution')
    if side == SIDE_BUY:
        return exchange.create_limit_buy_order(market, trading_amount, price)
    else:
        return exchange.create_limit_sell_order(market, trading_amount, price)
