import talib
import common
import numpy

ATR_PERIOD = 14


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


def mavilimBullAndBear(close, truncate):
    mavilimw_array = mavilimw(close=close)
    # Removing the first len(close) - length(mavilimw) of elements so its size will be same with MAVILIMW array.
    close = close[len(close) - len(mavilimw_array):]
    gap = numpy.subtract(close, mavilimw_array)  # Finding gap value by subtract close price to its MAVILIMW value.
    bull = []
    bear = []
    for x in gap:
        bull.append(x) if x >= 0 else bear.append(x)  # Diverging gap values according to be positive or negative.

    last_mavilimw = common.truncate(mavilimw_array[-2], decimals=truncate)  # Calculating last MAVILIMW value.
    # Calculating standard deviation of bullish gaps.
    stddev_bull = common.truncate(last_mavilimw + 2 * numpy.std(bull), decimals=truncate)
    # Calculating standard deviation of bearish gaps.
    stddev_bear = common.truncate(last_mavilimw - 2 * numpy.std(bear), decimals=truncate)
    return last_mavilimw, stddev_bull, stddev_bear
