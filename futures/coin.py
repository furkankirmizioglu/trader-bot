from binance import Client
from numpy import array
from scipy.stats import stats
import common
import database
from indicators import mavilimw_bullandbear, atr

PRICE_INTERVAL = Client.KLINE_INTERVAL_1HOUR


class Coin:
    pair = ""
    quantity = 0
    priceDec = 0
    qtyDec = 0
    candles = []
    lastPrice = 0
    prevPrice = 0
    atr = 0
    zScore = 0
    mavilimw = 0
    top = 0
    bottom = 0
    long = None
    short = None
    longHold = None
    shortHold = None
    hasLongOrder = None
    hasShortOrder = None

    def __init__(self, asset):
        self.pair = asset
        self.quantity = database.getQuantity(asset=self.pair)
        self.priceDec, self.qtyDec = database.getPrecision(asset=self.pair)
        self.long = database.getLong(asset=self.pair)
        self.short = database.getShort(asset=self.pair)
        self.candles = common.price_action(symbol=self.pair, interval=PRICE_INTERVAL)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimw_bullandbear(close=self.candles, truncate=4)
        self.zScore = common.truncate(stats.zscore(a=self.candles, axis=0, nan_policy='omit')[-1], 4)
        self.lastPrice = self.candles[-1]
        self.prevPrice = self.candles[-2]
        self.longHold = database.getLongHold(asset=self.pair)
        self.shortHold = database.getShortHold(asset=self.pair)
        self.hasLongOrder = database.getHasLongOrder(asset=self.pair)
        self.hasShortOrder = database.getHasShortOrder(asset=self.pair)
        del self.candles
