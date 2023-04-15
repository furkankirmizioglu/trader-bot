from talib import ATR, WMA
from futures_common import truncate
import numpy

ATR_PERIOD = 14


# Calculates and returns ATR (Average True Range) value.
def atr(klines):
    # x[2] => HIGH
    # x[3] => LOW
    # x[4] => CLOSE
    atr_list = ATR(numpy.array([float(x[2]) for x in klines]),
                   numpy.array([float(x[3]) for x in klines]),
                   numpy.array([float(x[4]) for x in klines]),
                   ATR_PERIOD)
    return truncate(atr_list[-1], 5)


# Calculates and returns MAVILIMW value.
def mavilimw(close):
    avg1 = WMA(close, 3)
    avg2 = WMA(avg1, 5)
    avg3 = WMA(avg2, 8)
    avg4 = WMA(avg3, 13)
    avg5 = WMA(avg4, 21)
    avg6 = WMA(avg5, 34)
    avg6 = avg6[numpy.logical_not(numpy.isnan(avg6))]
    return avg6


def mavilimBullAndBear(close, decimal):
    mavilimw_array = mavilimw(close=close)
    std = numpy.std(mavilimw_array)
    last_mavilimw = truncate(mavilimw_array[-2], decimals=decimal)  # Calculating last MAVILIMW value.
    # Calculating standard deviation of bullish gaps.
    stddev_bull = truncate(last_mavilimw + std, decimals=decimal)
    # Calculating standard deviation of bearish gaps.
    stddev_bear = truncate(last_mavilimw - std, decimals=decimal)
    return last_mavilimw, stddev_bull, stddev_bear
