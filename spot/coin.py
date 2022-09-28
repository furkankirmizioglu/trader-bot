from numpy import array
from scipy.stats import stats
import common
from constants import PRICE_INTERVAL
from database import getHoldFlags, getDecimalValues
from indicators import mavilimBullBear, atr
import asyncio


class Coin:
    pair = ""
    isLong = None
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

    async def isLongAndOpenOrders(self):
        self.hasBuyOrder, self.hasSellOrder = common.checkOpenOrder(asset=self.pair)
        self.isLong = common.checkPosition(asset=self.pair)
        self.buyFlag, self.sellFlag = getHoldFlags(asset=self.pair)

    async def pricesAndValues(self):
        self.priceDec, self.qtyDec = getDecimalValues(asset=self.pair)
        self.candles = common.priceActions(symbol=self.pair, interval=PRICE_INTERVAL)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimBullBear(close=self.candles, truncate=self.priceDec)
        self.zScore = common.truncate(stats.zscore(a=self.candles, axis=0, nan_policy='omit')[-1], self.priceDec)
        self.lastPrice = self.candles[-1]
        self.prevPrice = self.candles[-2]
        del self.candles

    async def mainTask(self):
        task1 = asyncio.create_task(self.isLongAndOpenOrders())
        task2 = asyncio.create_task(self.pricesAndValues())
        await task1
        await task2

    def __init__(self, pair):
        self.pair = pair
        asyncio.run(self.mainTask())
