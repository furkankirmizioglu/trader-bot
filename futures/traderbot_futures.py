# TRADES ON FUTURES MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import logging
import time
from datetime import datetime
from binance.client import Client
import futures_common as common
import futures_database as database
from futures_orders import futures_limit_order
from coin import Coin

logging.basicConfig(level=logging.INFO)
AMOUNT_V3 = 0
LEVERAGE = 5
coin_list = ['ETH', 'SOL']


def trader(coin):
    now = datetime.now().replace(microsecond=0)

    # BUY CONDITIONS.
    if coin.prevPrice > coin.mavilimw:
        if coin.long:
            pass
        elif coin.hasLongOrder:
            pass
        elif coin.longHold:
            pass
        else:
            if coin.short:
                # TODO -> Close short pos. before entering long.
                database.set_short(asset=coin.pair, isShort=False)
                # Son fiyat - ATR değeri hesaplanır. Bu limit alım yeridir.
            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Alım yapılacak coin miktarı belirlenir. Alımı engellememek için stop alım fiyatından hesaplanır.
            quantity = common.truncate(AMOUNT_V3 * LEVERAGE / limit, coin.qtyDec)
            # Alım emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            futures_limit_order(now=now, pair=coin.pair,
                                side=Client.SIDE_BUY,
                                quantity=quantity,
                                limit=limit)
            database.set_long(asset=coin.pair, isLong=True)

    elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
        if coin.long:
            pass
        elif coin.hasLongOrder:
            # TODO -> Print already have an order log to terminal.
            pass
        elif coin.hold:
            pass
        else:
            if coin.short:
                # TODO -> Close short pos. before entering long.
                database.set_short(asset=coin.pair, isShort=False)
            # Son fiyat - ATR değeri hesaplanır. Bu limit alım yeridir.
            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Alım yapılacak coin miktarı belirlenir. Alımı engellememek için stop alım fiyatından hesaplanır.
            quantity = common.truncate(AMOUNT_V3 * LEVERAGE / limit, coin.qtyDec)
            # Alım emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            futures_limit_order(now=now, pair=coin.pair,
                                side=Client.SIDE_BUY,
                                quantity=quantity,
                                limit=limit)
            database.set_long(asset=coin.pair, isLong=True)
            database.set_short_hold(asset=coin.pair, hold=True)

    # SELL CONDITIONS.
    if coin.prevPrice < coin.mavilimw:
        if coin.short:
            pass
        elif coin.hasShortOrder:
            # TODO -> Print already have an order log to terminal.
            pass
        elif coin.shortHold:
            pass
        else:
            if coin.long:
                # TODO -> Close long position before entering long.
                database.set_long(asset=coin.pair, isLong=False)
            # Son fiyat + ATR değeri hesaplanır. Bu limit satış yeridir.
            limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            quantity = common.truncate(common.wallet(asset=coin.pair), coin.qtyDec)
            # Satış emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            futures_limit_order(now=now, pair=coin.pair,
                                side=Client.SIDE_SELL,
                                quantity=quantity,
                                limit=limit)
            database.set_short(asset=coin.pair, isShort=True)

    elif coin.zScore > 1.5 and coin.lastPrice > coin.top:
        if coin.short:
            pass
        elif coin.hasShortOrder:
            # TODO -> Print already have an order log to terminal.
            pass
        elif coin.hold:
            pass
        else:
            if coin.long:
                # TODO -> Close long position before entering long.
                database.set_long(asset=coin.pair, isLong=False)
            # Son fiyat + ATR değeri hesaplanır. Bu limit satış yeridir.
            limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            quantity = common.truncate(common.wallet(asset=coin.pair), coin.qtyDec)
            # Satış emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            futures_limit_order(now=now, pair=coin.pair,
                                side=Client.SIDE_SELL,
                                quantity=quantity,
                                limit=limit)
            database.set_short(asset=coin.pair, isShort=True)
            database.set_long_hold(asset=coin.pair, hold=True)

    # Önceki kapanış fiyatı mavilimw'i yukarı keserse ve sat flag'i 0 ise satış yapmasına izin verilir.
    if coin.prevPrice > coin.mavilimw and coin.shortHold:
        database.set_short_hold(asset=coin.pair, hold=False)
    # Önceki kapanış fiyatı mavilimw'i aşağı keserse ve al flag'i 0 ise alım yapmasına izin verilir.
    elif coin.prevPrice < coin.mavilimw and coin.longHold:
        database.set_long_hold(asset=coin.pair, hold=False)


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global coin_list, AMOUNT_V3
    for coin in coin_list:
        coin_list[coin_list.index(coin)] = coin + common.BUSD
    if common.initializer(pair_list=coin_list):
        logging.info(common.HAVE_ASSET_LOG.format(', '.join(common.initializer(pair_list=coin_list))))
    while 1:
        AMOUNT_V3 = common.usd_alloc(coin_list)
        for coin in coin_list:
            if common.position_control(asset=coin, position_side="LONG"):
                database.set_long(asset=coin, isLong=True)
            elif common.position_control(asset=coin, position_side="SHORT"):
                database.set_short(asset=coin, isShort=True)
            while 1:
                try:
                    trader(coin=Coin(asset=coin))
                    time.sleep(5)
                    break
                except Exception as e:
                    print(e)
                    break


start_now = datetime.now().replace(microsecond=0)
# common.tweet(common.START_LOG.format(start_now, ", ".join(asset_list)))
logging.info(common.START_LOG.format(start_now, ", ".join(coin_list)))
bot()
