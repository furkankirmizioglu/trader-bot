from numpy import array
from scipy.stats import stats
import common
from constants import PRICE_INTERVAL
from indicators import mavilimBullBear, atr
import asyncio
import database


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
    buyHold = ""
    sellHold = ""
    hasBuyOrder = None
    hasSellOrder = None

    async def isLongAndOpenOrders(self, queryResponse):
        self.hasBuyOrder, self.hasSellOrder = common.checkOpenOrder(pair=self.pair)
        self.isLong = common.checkPosition(pair=self.pair)
        self.buyHold = queryResponse[5]
        self.sellHold = queryResponse[6]
        COLUMNS = ['IS_LONG', 'HAS_BUY_ORDER', 'HAS_SELL_ORDER']
        database.bulkUpdatePrmOrder(pair=self.pair, columns=COLUMNS,
                                    values=(self.isLong, self.hasBuyOrder, self.hasSellOrder))

    async def pricesAndValues(self, queryResponse):
        self.priceDec = queryResponse[1]
        self.qtyDec = queryResponse[2]
        self.candles = common.priceActions(pair=self.pair, interval=PRICE_INTERVAL)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimBullBear(close=self.candles, truncate=self.priceDec)
        self.zScore = common.truncate(stats.zscore(a=self.candles, axis=0, nan_policy='omit')[-1], self.priceDec)
        self.lastPrice = self.candles[-1]
        self.prevPrice = self.candles[-2]
        del self.candles

    async def mainTask(self):
        query = database.selectAllFromPrmOrder(pair=self.pair)[-1]
        task1 = asyncio.create_task(self.isLongAndOpenOrders(query))
        task2 = asyncio.create_task(self.pricesAndValues(query))
        await task1
        await task2

    def __init__(self, pair):
        self.pair = pair
        asyncio.run(self.mainTask())
