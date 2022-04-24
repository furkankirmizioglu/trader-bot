# TRADES ON FUTURES MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import logging
import time
from datetime import datetime
from binance.client import Client
import common as common
import constants
import database as database
from orders import stopMarketOrder, takeProfitMarketOrder, marketOrder
from coin import Coin

logging.basicConfig(level=logging.INFO)
AMOUNT_V3 = 0
pairList = ['DYDXUSDT']


def trader(coin):
    global AMOUNT_V3
    start = time.time()
    coin = Coin(asset=coin)

    # LONG CONDITIONS.
    if coin.prevPrice > coin.mavilimw:
        if coin.long or coin.hasLongOrder or coin.longHold:
            pass
        else:
            if coin.short:
                # Before submit a long position order, close short position.
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                stopMarketPrice = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
                takeProfitMarketPrice = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
                stopMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, stopPrice=stopMarketPrice)
                takeProfitMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, stopPrice=takeProfitMarketPrice)
                common.tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, 'LONG', coin.pair, stopMarketPrice,
                                                                       takeProfitMarketPrice))
                database.setHasLongOrder(asset=coin.pair, hasLongOrder=True)
            else:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                quantity = common.truncate(AMOUNT_V3 * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
                marketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, quantity=quantity, logPrice=coin.lastPrice)
                database.setLong(asset=coin.pair, isLong=True)
                logging.info(constants.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
        if coin.long or coin.hasLongOrder or coin.longHold:
            pass
        else:
            if coin.short:
                # Before submit a long position order, close short position.
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                stopMarketPrice = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
                takeProfitMarketPrice = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
                stopMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, stopPrice=stopMarketPrice)
                takeProfitMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, stopPrice=takeProfitMarketPrice)
                common.tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, 'LONG', coin.pair, stopMarketPrice,
                                                                       takeProfitMarketPrice))
                database.setHasLongOrder(asset=coin.pair, hasLongOrder=True)
            else:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                quantity = common.truncate(AMOUNT_V3 * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
                marketOrder(now=now, pair=coin.pair, side=Client.SIDE_BUY, quantity=quantity, logPrice=coin.lastPrice)
                database.setLong(asset=coin.pair, isLong=True)
                database.setShortHold(asset=coin.pair, hold=True)
                logging.info(constants.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # SHORT CONDITIONS.
    if coin.prevPrice < coin.mavilimw:
        if coin.short or coin.hasShortOrder or coin.shortHold:
            pass
        else:
            if coin.long:
                # Before submit a short order, close long position immediately.
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                stopMarketPrice = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
                takeProfitMarketPrice = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
                stopMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, stopPrice=stopMarketPrice)
                takeProfitMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, stopPrice=takeProfitMarketPrice)
                common.tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, 'LONG', coin.pair, stopMarketPrice,
                                                                       takeProfitMarketPrice))
                database.setHasShortOrder(asset=coin.pair, hasShortOrder=True)
            else:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                quantity = common.truncate(AMOUNT_V3 * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
                marketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, quantity=quantity, logPrice=coin.lastPrice)
                database.setShort(asset=coin.pair, isShort=True)
                logging.info(constants.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    elif coin.zScore > 1.5 and coin.lastPrice > coin.top:
        if coin.short or coin.hasShortOrder or coin.shortHold:
            pass
        else:
            if coin.long:
                # Before submit a short order, close long position immediately.
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                stopMarketPrice = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
                takeProfitMarketPrice = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
                stopMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, stopPrice=stopMarketPrice)
                takeProfitMarketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, stopPrice=takeProfitMarketPrice)
                common.tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, 'LONG', coin.pair, stopMarketPrice,
                                                                       takeProfitMarketPrice))
                database.setHasShortOrder(asset=coin.pair, hasShortOrder=True)
            else:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                quantity = common.truncate(AMOUNT_V3 * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
                marketOrder(now=now, pair=coin.pair, side=Client.SIDE_SELL, quantity=quantity, logPrice=coin.lastPrice)
                database.setHasShortOrder(asset=coin.pair, hasShortOrder=True)
                database.setLongHold(asset=coin.pair, hold=True)
                logging.info(constants.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    if coin.prevPrice > coin.mavilimw and coin.shortHold:
        database.setShortHold(asset=coin.pair, hold=False)

    elif coin.prevPrice < coin.mavilimw and coin.longHold:
        database.setLongHold(asset=coin.pair, hold=False)


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global pairList, AMOUNT_V3
    hasLongPosList, hasShortPosList = common.initializer(pair_list=pairList)
    if len(hasLongPosList) > 0:
        logging.info(constants.LONG_POSITION_LOG.format(', '.join(hasLongPosList)))
    if len(hasShortPosList) > 0:
        logging.info(constants.SHORT_POSITION_LOG.format(', '.join(hasShortPosList)))
    while 1:
        while 1:
            for coin in pairList:
                try:
                    AMOUNT_V3 = common.usd_alloc(pairList)

                    hasLongOrder = common.open_order_control(asset=coin, order_side='BUY')
                    hasShortOrder = common.open_order_control(asset=coin, order_side='SELL')

                    database.setHasLongOrder(asset=coin, hasLongOrder=hasLongOrder)
                    database.setHasShortOrder(asset=coin, hasShortOrder=hasShortOrder)

                    isLong, isShort, quantity = common.check_position(asset=coin)

                    database.setLong(asset=coin, isLong=isLong)
                    database.setShort(asset=coin, isShort=isShort)
                    database.setQuantity(asset=coin, quantity=quantity)

                    trader(coin=coin)
                    time.sleep(5)
                except Exception as e:
                    print(e)
                else:
                    pass


start_now = datetime.now().replace(microsecond=0)
# common.tweet(constants.START_LOG.format(start_now, ", ".join(pairList)))
logging.info(constants.START_LOG.format(start_now, ", ".join(pairList)))
bot()
