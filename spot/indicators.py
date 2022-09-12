import talib
import common
import numpy

from constants import RSI_PERIOD, ATR_PERIOD


# Calculates and returns RSI (Relative Strength Index) value.
def rsi(klines):
    rsi_list = talib.RSI([float(x[4]) for x in klines], RSI_PERIOD)
    return common.truncate(rsi_list[-1], 2)


# Calculates and returns ATR (Average True Range) value.
def atr(klines):
    # x[2] = HIGH
    # x[3] = LOW
    # x[4] = CLOSE
    atr_list = talib.ATR(numpy.array([float(x[2]) for x in klines]),
                         numpy.array([float(x[3]) for x in klines]),
                         numpy.array([float(x[4]) for x in klines]),
                         ATR_PERIOD)
    return common.truncate(atr_list[-1], 5)


# Calculates and returns last MA (Moving Average) value.
def ma(klines, period):
    ma_list = talib.MA([float(x[4]) for x in klines], period)
    return common.truncate(ma_list[-1], 5)


# Calculates and returns MAVILIMW value.
def mavilimw(close):
    avg1 = talib.WMA(close, 3)
    avg2 = talib.WMA(avg1, 5)
    avg3 = talib.WMA(avg2, 8)
    avg4 = talib.WMA(avg3, 13)
    avg5 = talib.WMA(avg4, 21)
    avg6 = talib.WMA(avg5, 34)
    avg6 = avg6[numpy.logical_not(numpy.isnan(avg6))]
    return avg6


def mavilimw_bullandbear(close, truncate):
    mavilimw_array = mavilimw(close=close)
    # Removing the first len(close) - length(mavilimw) of elements so its size will be same with MAVILIMW array.
    close = close[len(close) - len(mavilimw_array):]
    gap = numpy.subtract(close, mavilimw_array)  # Finding gap value by subtract close price to its MAVILIMW value.
    bull = []
    bear = []
    for x in gap:
        bull.append(x) if x >= 0 else bear.append(x)  # Diverging gap values according to be positive or negative.

    last_mavilimw = common.truncate(mavilimw_array[-1], decimals=truncate)  # Calculating last MAVILIMW value.
    # Calculating standard deviation of bullish gaps.
    stddev_bull = common.truncate(last_mavilimw + 2 * numpy.std(bull), decimals=truncate)
    # Calculating standard deviation of bearish gaps.
    stddev_bear = common.truncate(last_mavilimw - 2 * numpy.std(bear), decimals=truncate)
    return last_mavilimw, stddev_bull, stddev_bear


def macd(klines):
    macd, macd_signal, macd_hist = talib.MACD(numpy.array([float(x[4]) for x in klines]), 12, 26, 9)
    return macd, macd_signal, macd_hist


# Calculates and returns EMA (Exponential Moving Average) value.
def ema(klines, period):
    ema_list = talib.EMA([float(x[4]) for x in klines], period)
    return common.truncate(ema_list[-1], 5)


# Calculates last EMA, standard deviations of + and - gaps between price and its MA value.
def bullandbear(close, period, truncate):
    ema_arr = talib.EMA(numpy.array(close), period)  # Calculating MA
    ema_arr = ema_arr[numpy.logical_not(numpy.isnan(ema_arr))]  # Removing NaN values from EMA array.
    close = close[period - 1:]  # Removing first period - 1 elements so its size will be same with EMA array.
    gap = numpy.subtract(close, ema_arr)  # Finding gap value by subtract close price to its EMA value.
    bull = []
    bear = []
    for x in gap:
        bull.append(x) if x >= 0 else bear.append(x)  # Diverging gap values according to be positive or negative.

    ema = common.truncate(ema_arr[-2], decimals=truncate)
    # Calculating standard deviation of bullish gaps.
    stddev_bull = common.truncate(ema + numpy.std(bull), decimals=truncate)
    # Calculating standard deviation of bearish gaps.
    stddev_bear = common.truncate(ema - numpy.std(bear), decimals=truncate)
    return ema, stddev_bull, stddev_bear


# Calculates RSI cross
def rsi_cross(klines, long, short, ema_period):
    close = numpy.array([float(x[4]) for x in klines])
    long_ema_rsi = talib.EMA(talib.RSI(close, long), ema_period)
    short_ema_rsi = talib.EMA(talib.RSI(close, short), ema_period)
    return long_ema_rsi[-2], short_ema_rsi[-2]
