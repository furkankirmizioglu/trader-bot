from numpy import array
from scipy.stats import stats
import common
import constants
import database
from constants import SIDE_BUY, SIDE_SELL
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

    def __init__(self, pair):
        isLong = common.position_control(asset=pair)
        database.set_islong(asset=pair, isLong=isLong)
        hasBuyOrder = common.open_order_control(asset=pair, order_side=SIDE_BUY)
        database.set_hasBuyOrder(asset=pair, hasBuyOrder=hasBuyOrder)
        hasSellOrder = common.open_order_control(asset=pair, order_side=SIDE_SELL)
        database.set_hasSellOrder(asset=pair, hasSellOrder=hasSellOrder)
        self.pair = pair
        self.priceDec, self.qtyDec = database.get_decimals(asset=self.pair)
        self.candles = common.price_action(symbol=self.pair, interval=constants.PRICE_INTERVAL)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimw_bullandbear(close=self.candles, truncate=self.priceDec)
        self.zScore = common.truncate(stats.zscore(a=self.candles, axis=0, nan_policy='omit')[-1], self.priceDec)
        self.lastPrice = self.candles[-1]
        self.prevPrice = self.candles[-2]
        self.buyFlag, self.sellFlag = database.get_orderFlag(asset=self.pair)
        self.is_long = isLong
        self.hasBuyOrder = hasBuyOrder
        self.hasSellOrder = hasSellOrder
        del self.candles
