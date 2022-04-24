# TRADES ON FUTURES MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import logging
import time
from datetime import datetime
from binance.client import Client
import common as common
import database as database
from orders import limit_order, market_order
from coin import Coin

logging.basicConfig(level=logging.INFO)
AMOUNT_V3 = 0
pairList = ['DYDXUSDT']


def trader(coin):
    global AMOUNT_V3
    start = time.time()
    coin = Coin(asset=coin)

    # BUY CONDITIONS.
    if coin.prevPrice > coin.mavilimw:
        if coin.long or coin.hasLongOrder or coin.longHold:
            pass
        else:
            if coin.short:
                # Before submit a long position order, close short position immediately.
                market_order(pair=coin.pair, side=Client.SIDE_BUY, quantity=coin.quantity, logPrice=coin.lastPrice)
                database.set_short(asset=coin.pair, isShort=False)
                AMOUNT_V3 = common.usd_alloc(asset_list=pairList)

            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            quantity = common.truncate(AMOUNT_V3 * common.LEVERAGE / limit, coin.qtyDec)
            limit_order(pair=coin.pair, side=Client.SIDE_BUY, quantity=quantity, limit=limit)

            database.set_hasLongOrder(asset=coin.pair, hasLongOrder=True)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
        if coin.long or coin.hasLongOrder or coin.longHold:
            pass
        else:
            if coin.short:
                # Before submit a long position order, close short position immediately.
                market_order(pair=coin.pair, side=Client.SIDE_BUY, quantity=coin.quantity, logPrice=coin.lastPrice)
                database.set_short(asset=coin.pair, isShort=False)
                AMOUNT_V3 = common.usd_alloc(asset_list=pairList)

            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            quantity = common.truncate(AMOUNT_V3 * common.LEVERAGE / limit, coin.qtyDec)
            limit_order(pair=coin.pair, side=Client.SIDE_BUY, quantity=quantity, limit=limit)

            database.set_hasLongOrder(asset=coin.pair, hasLongOrder=True)
            database.set_short_hold(asset=coin.pair, hold=True)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # SELL CONDITIONS.
    if coin.prevPrice < coin.mavilimw:
        if coin.short or coin.hasShortOrder or coin.shortHold:
            pass
        else:
            if coin.long:
                # Before submit a short order, close long position immediately.
                market_order(pair=coin.pair, side=Client.SIDE_SELL, quantity=coin.quantity, logPrice=coin.lastPrice)
                database.set_long(asset=coin.pair, isLong=False)
                AMOUNT_V3 = common.usd_alloc(asset_list=pairList)

            limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            quantity = common.truncate(AMOUNT_V3 * common.LEVERAGE / limit, coin.qtyDec)
            limit_order(pair=coin.pair, side=Client.SIDE_SELL, quantity=quantity, limit=limit)

            database.set_hasShortOrder(asset=coin.pair, hasShortOrder=True)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    elif coin.zScore > 1.5 and coin.lastPrice > coin.top:
        if coin.short or coin.hasShortOrder or coin.shortHold:
            pass
        else:
            if coin.long:
                # Before submit a short order, close long position immediately.
                market_order(pair=coin.pair, side=Client.SIDE_SELL, quantity=coin.quantity, logPrice=coin.lastPrice)
                database.set_long(asset=coin.pair, isLong=False)
                AMOUNT_V3 = common.usd_alloc(asset_list=pairList)

            limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            quantity = common.truncate(AMOUNT_V3 * common.LEVERAGE / limit, coin.qtyDec)
            limit_order(pair=coin.pair, side=Client.SIDE_SELL, quantity=quantity, limit=limit)

            database.set_hasShortOrder(asset=coin.pair, hasShortOrder=True)
            database.set_long_hold(asset=coin.pair, hold=True)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    if coin.prevPrice > coin.mavilimw and coin.shortHold:
        database.set_short_hold(asset=coin.pair, hold=False)

    elif coin.prevPrice < coin.mavilimw and coin.longHold:
        database.set_long_hold(asset=coin.pair, hold=False)


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global pairList, AMOUNT_V3
    hasLongPosList, hasShortPosList = common.initializer(pair_list=pairList)
    if len(hasLongPosList) > 0:
        logging.info(common.LONG_POSITION_LOG.format(', '.join(hasLongPosList)))
    if len(hasShortPosList) > 0:
        logging.info(common.SHORT_POSITION_LOG.format(', '.join(hasShortPosList)))
    while 1:
        while 1:
            for coin in pairList:
                try:
                    AMOUNT_V3 = common.usd_alloc(pairList)

                    hasLongOrder = common.open_order_control(asset=coin, order_side='BUY')
                    hasShortOrder = common.open_order_control(asset=coin, order_side='SELL')

                    database.set_hasLongOrder(asset=coin, hasLongOrder=hasLongOrder)
                    database.set_hasShortOrder(asset=coin, hasShortOrder=hasShortOrder)

                    isLong, isShort, quantity = common.check_position(asset=coin)

                    database.set_long(asset=coin, isLong=isLong)
                    database.set_short(asset=coin, isShort=isShort)
                    database.set_quantity(asset=coin, quantity=quantity)

                    trader(coin=coin)
                    time.sleep(5)
                except Exception as e:
                    print(e)
                else:
                    pass


start_now = datetime.now().replace(microsecond=0)
# common.tweet(common.START_LOG.format(start_now, ", ".join(asset_list)))
logging.info(common.START_LOG.format(start_now, ", ".join(pairList)))
bot()
