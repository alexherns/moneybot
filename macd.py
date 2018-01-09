import math
import pandas as pd
import market as mkt

SELL_FRACTION = 1.0
BUY_FRACTION = 0.45

def find_and_act_on_markets(exchange, logger, timeframe='30m', ma1=12, ma2=26):
    # TODO: will eventually move this to a system where the markets can be detected based on the momersion index
    # and the currencies that we have already invested in
    markets = ['XRP/ETH']
    orders = []
    for market in markets:
        logger.info('evaluating market for behavior')
        behavior = predict_behavior(exchange, market, timeframe, ma1, ma2)
        logger.info('behavior predicted %s', behavior)
        limits = mkt.fetch_limits(exchange, market)
        logger.info('limits %s', str(limits))
        balance = exchange.fetch_free_balance()
        ticker = exchange.fetchTicker(market)
        amount = get_trading_amount(logger, limits, market, behavior, balance, ticker)
        logger.info('amount predicted %s', str(amount))
        order = mkt.execute_market_trade(exchange, market, behavior, amount)
        if order is None:
            logger.info('No trades to be made')
        orders.append(order)
    return orders


def predict_behavior(exchange, market, timeframe, ma1, ma2):
    if ma1 >= ma2:
        raise Exception('ma1 must be less than ma2')
    if ma2 > 200:
        raise Exception('ma2 may not be larger than 200')
    ohlcv_data = exchange.fetch_ohlcv(
        market, limit=ma2 * 2, timeframe=timeframe)
    return _predict_mkt_data(ohlcv_data, ma1=ma1, ma2=ma2)


def _predict_mkt_data(ohlcv_data, ma1, ma2):
    opening_prices = pd.Series(
        [row[1] for row in ohlcv_data])
    rolling_ma1 = list(opening_prices.rolling(window=ma1, center=False).mean())
    rolling_ma2 = list(opening_prices.rolling(window=ma2, center=False).mean())
    if rolling_ma1[-1] > rolling_ma2[-1] and rolling_ma1[-2] < rolling_ma2[-2]:
        return mkt.SIDE_BUY
    elif rolling_ma1[-1] < rolling_ma2[-1] and rolling_ma1[-2] > rolling_ma2[-2]:
        return mkt.SIDE_SELL
    return mkt.SIDE_HODL

def get_trading_amount(logger, limits, market, side, balance, ticker):
    if side == mkt.SIDE_HODL:
        return None
    elif side not in (mkt.SIDE_BUY, mkt.SIDE_SELL):
        raise Exception('Unknown side for execution')
    if side == mkt.SIDE_BUY:
        purchasing_currency = market.split('/')[1]
        purchasing_funds = balance[purchasing_currency] * BUY_FRACTION
        trade_amount = purchasing_funds * ticker['ask']
        logger.info('buying %s with %s at %s with %s gives %s total', market.split('/')[0], purchasing_currency, ticker['ask'], purchasing_funds, trade_amount)
    elif side == mkt.SIDE_SELL:
        sell_currency = market.split('/')[0]
        trade_amount = balance[sell_currency] * SELL_FRACTION
        logger.info('selling %s for %s gives %s total', sell_currency, market.split('/')[0], trade_amount)
    trade_amount = math.floor(trade_amount / limits.price_filter.tick_size) * \
        limits.price_filter.tick_size
    logger.info('funds available results in %s sale', trade_amount)
    if trade_amount < limits.lot_size.min_qty:
        return None
    return trade_amount
