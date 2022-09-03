from numpy import array
from scipy.stats import stats
import common
import database
from indicators import mavilimw_bullandbear, atr


class Coin:
    pair = ""
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
    buyFlag = ""
    sellFlag = ""
    hasBuyOrder = None
    hasSellOrder = None

    def __init__(self, asset, interval):
        self.pair = asset
        isLong = common.position_control(asset=asset)
        database.set_islong(asset=asset, isLong=isLong)
        self.is_long = database.get_islong(asset=self.pair)
        self.priceDec, self.qtyDec = database.get_decimals(asset=self.pair)
        self.candles = common.price_action(symbol=self.pair, interval=interval)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimw_bullandbear(close=self.candles, truncate=self.priceDec)
        self.zScore = common.truncate(stats.zscore(a=self.candles, axis=0, nan_policy='omit')[-1], self.priceDec)
        self.lastPrice = self.candles[-1]
        self.prevPrice = self.candles[-2]
        self.buyFlag, self.sellFlag = database.get_orderFlag(asset=self.pair)
        hasBuyOrder = common.open_order_control(asset=asset, order_side='BUY')
        database.set_hasBuyOrder(asset=asset, hasBuyOrder=hasBuyOrder)
        self.hasBuyOrder = database.get_hasBuyOrder(asset=self.pair)
        self.hasSellOrder = database.get_hasSellOrder(asset=self.pair)
        hasSellOrder = common.open_order_control(asset=asset, order_side='SELL')
        database.set_hasSellOrder(asset=asset, hasSellOrder=hasSellOrder)
        del self.candles
