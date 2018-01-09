import pandas as pd
import common


def predict_behavior(exchange, market, timeframe='30m', ma1=12, ma2=26):
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
        return common.SIDE_BUY
    elif rolling_ma1[-1] < rolling_ma2[-1] and rolling_ma1[-2] > rolling_ma2[-2]:
        return common.SIDE_SELL
    return common.SIDE_HODL
