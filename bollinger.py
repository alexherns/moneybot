import pandas as pd
import common


def predict_behavior(exchange, market, timeframe='30m', window_size=20, band_factor=2.0):
    ohlcv_data = exchange.fetch_ohlcv(
        market, limit=window_size, timeframe=timeframe)
    ticker_data = exchange.fetch_ticker(market)
    return _predict_mkt_data(ohlcv_data, ticker_data, band_factor=band_factor)


def _predict_mkt_data(ohlcv_data, ticker_data, band_factor):
    closing_prices = pd.Series(
        [row[4] for row in ohlcv_data])

    sma = closing_prices.mean()
    stdev = closing_prices.std()
    upper_band = sma + stdev * band_factor
    lower_band = sma - stdev * band_factor
    return upper_band, lower_band
