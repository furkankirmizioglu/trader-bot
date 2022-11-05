from binance import Client
from numpy import array
from scipy.stats import stats
import common
import database
from indicators import mavilimBullAndBear, atr

PRICE_INTERVAL = Client.KLINE_INTERVAL_1HOUR


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
    long = None
    short = None
    quantity = 0
    longHold = None
    shortHold = None
    hasLongOrder = None
    hasShortOrder = None

    async def isLongAndOpenOrders(self, queryResponse):
        self.hasLongOrder = common.checkOpenOrder(pair=self.pair, order_side="LONG")
        self.hasShortOrder = common.checkOpenOrder(pair=self.pair, order_side="SHORT")
        self.long = queryResponse[4]
        self.short = queryResponse[5]
        self.quantity = queryResponse[6]
        self.longHold = queryResponse[7]
        self.shortHold = queryResponse[8]

    async def pricesAndValues(self, queryResponse):
        self.priceDec = queryResponse[1]
        self.qtyDec = queryResponse[2]
        self.candles = common.priceActions(pair=self.pair, interval=constants.PRICE_INTERVAL)
        self.atr = atr(klines=self.candles)
        self.candles = array([float(x[4]) for x in self.candles])
        self.mavilimw, self.top, self.bottom = mavilimBullAndBear(close=self.candles, truncate=self.priceDec)
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
