# TRADES ON SPOT MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import logging
import time
from datetime import datetime
from binance.client import Client
import common
import database
from coin import Coin

logging.basicConfig(level=logging.INFO)
AMOUNT_V3 = 0
coin_list = ['CRV', 'DYDX']


def trader(coin):
    start = time.time()
    now = datetime.now().replace(microsecond=0)
    # BUY CONDITIONS.
    if not coin.is_long and coin.buyFlag == 1:  # Long pozisyon yoksa ve alım flag'i 1 ise buraya girilir.

        # Önceden girilmiş alım emri varsa terminale log atılır ve çıkılır.
        if coin.hasLongOrder:
            if coin.prevPrice < coin.mavilimw:
                common.cancel_order(asset=coin.pair, order_side=Client.SIDE_BUY)
            else:
                logging.info(common.OPEN_ORDER_LOG.format(now, coin.pair, Client.SIDE_BUY))

        # Önceki kapanış fiyatı mavilimw'i yukarı kestiyse ve alım flag == 1 ise long pozisyon emri girilir.
        elif coin.prevPrice > coin.mavilimw:
            if AMOUNT_V3 < common.MIN_USD:
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))
            # Son fiyat - ATR değeri hesaplanır. Bu limit alım yeridir.
            target = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Son fiyat + ATR değerinin %2 eksiğine stop trigger girilir.
            stop = common.truncate(coin.prevPrice + (coin.atr * 98 / 100), coin.priceDec)
            # Son fiyattan bir ATR değeri fazlası hesaplanır. Bu stop alım yeridir.
            stop_limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            # Alım yapılacak coin miktarı belirlenir. Alımı engellememek için stop alım fiyatından hesaplanır.
            quantity = common.truncate(AMOUNT_V3 / stop_limit, coin.qtyDec)
            # Alım emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            # oco_order(pair=coin.pair,
            #           side=Client.SIDE_BUY,
            #           quantity=quantity,
            #           oco_price=target,
            #           stop=stop,
            #           stop_limit=stop_limit)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

        # Z-SCORE -1'den küçük, son fiyat dip değerden düşük ve alım flag == 1 ise long pozisyon emri girilir.
        # Bu sırada fiyat mavilim'den düşük olduğu için satış yapılmasına izin verilmez. Satış flag'i 0 olarak girilir.
        elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
            if AMOUNT_V3 < common.MIN_USD:
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))
            # Son fiyat - ATR değeri hesaplanır. Bu limit alım yeridir.
            target = common.truncate(coin.lastPrice - coin.atr, coin.priceDec)
            # Son fiyat + ATR değerinin %2 eksiği hesaplanır. Bu stop trigger yeridir.
            stop = common.truncate(coin.lastPrice + (coin.atr * 98 / 100), coin.priceDec)
            # Son fiyat + ATR değeri hesaplanır. Bu stop alım yeridir.
            stop_limit = common.truncate(coin.lastPrice + coin.atr, coin.priceDec)
            # Alım yapılacak coin miktarı belirlenir. Alımı engellememek için stop alım fiyatından hesaplanır.
            quantity = common.truncate(AMOUNT_V3 / stop_limit, coin.qtyDec)
            # Alım emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            # oco_order(pair=coin.pair,
            #           side=Client.SIDE_BUY,
            #           quantity=quantity,
            #           oco_price=target,
            #           stop=stop,
            #           stop_limit=stop_limit)
            database.set_order_flag(asset=coin.pair, side=Client.SIDE_SELL, flag=0)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # SELL CONDITIONS.
    elif coin.is_long and coin.sellFlag == 1:  # Long pozisyon varsa buraya girilir.

        # Önceden girilmiş satış emri varsa terminale log atılır ve çıkılır.
        if coin.hasShortOrder:
            if coin.prevPrice > coin.mavilimw:
                common.cancel_order(asset=coin.pair, order_side=Client.SIDE_SELL)
            else:
                logging.info(common.OPEN_ORDER_LOG.format(now, coin.pair, Client.SIDE_SELL))

        # Bir önceki kapanış fiyatı mavilimden düşükse, ve satış flag == 1 ise satış yapılır.
        elif coin.prevPrice < coin.mavilimw:
            # Son fiyat + ATR değeri hesaplanır. Bu limit satış yeridir.
            target = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            # Son fiyat - ATR değerinin %2 fazlası hesaplanır. Bu stop trigger yeridir.
            stop = common.truncate(coin.prevPrice - (coin.atr * 98 / 100), coin.priceDec)
            # Son fiyat - ATR değeri hesaplanır. Bu stop satış yeridir.
            stop_limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Satış yapılacak coin adedi spot cüzdandan çekilir.
            quantity = common.truncate(common.wallet(asset=coin.pair), coin.qtyDec)
            # Satış emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            # oco_order(pair=coin.pair,
            #           side=Client.SIDE_SELL,
            #           quantity=quantity,
            #           oco_price=target,
            #           stop=stop,
            #           stop_limit=stop_limit)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

        # Z puanı 1.5'ten büyük, son fiyat tepe değerden büyükse tepe satışı yapılır.
        # Son fiyat mavilimin üstünde olduğundan alım yapmaması için alım flag'i 0 olarak setlenir.
        elif coin.zScore > 1.5 and coin.lastPrice > coin.top:
            # Son fiyat + ATR değeri hesaplanır. Bu limit satış yeridir.
            target = common.truncate(coin.lastPrice + coin.atr, coin.priceDec)
            # Son fiyat - ATR değerinin %2 fazlası hesaplanır. Bu stop trigger yeridir.
            stop = common.truncate(coin.lastPrice - (coin.atr * 98 / 100), coin.priceDec)
            # Son fiyat - ATR değeri hesaplanır. Bu stop satış yeridir.
            stop_limit = common.truncate(coin.lastPrice - coin.atr, coin.priceDec)
            # Satış yapılacak coin adedi spot cüzdandan çekilir.
            quantity = common.truncate(common.wallet(asset=coin.pair), coin.qtyDec)
            # Satış emri Binance'a iletilir. Tweet atılır, ORDER_LOG tablosu ve terminale log yazdırılır.
            # oco_order(pair=coin.pair,
            #           side=Client.SIDE_SELL,
            #           quantity=quantity,
            #           oco_price=target,
            #           stop=stop,
            #           stop_limit=stop_limit)
            database.set_order_flag(asset=coin.pair, side=Client.SIDE_BUY, flag=0)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # Önceki kapanış fiyatı mavilimw'i yukarı keser, sat flag'i 0 ise ve alım emri yoksa satış yapmasına izin verilir.
    if coin.prevPrice > coin.mavilimw and coin.sellFlag == 0:
        database.set_order_flag(asset=coin.pair, side=Client.SIDE_SELL, flag=1)
    # Önceki kapanış fiyatı mavilimw'i aşağı keserse ve al flag'i 0 ise alım yapmasına izin verilir.
    elif coin.prevPrice < coin.mavilimw and coin.buyFlag == 0:
        database.set_order_flag(asset=coin.pair, side=Client.SIDE_BUY, flag=1)


def initializer(pair_list):
    has_long = []
    for coin in pair_list:
        database.init_data(asset=coin)
        if common.position_control(asset=coin):
            database.set_islong(asset=coin, isLong=True)
            database.init_order_flag(asset=coin, isLong=True)
            has_long.append(coin)
        else:
            database.set_islong(asset=coin, isLong=False)
            database.init_order_flag(asset=coin, isLong=False)
    return has_long


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global coin_list, AMOUNT_V3
    for coin in coin_list:
        coin_list[coin_list.index(coin)] = coin + common.BUSD
    if initializer(pair_list=coin_list):
        logging.info(common.HAVE_ASSET_LOG.format(', '.join(initializer(pair_list=coin_list))))
    while 1:
        AMOUNT_V3 = common.usd_alloc(coin_list)
        for coin in coin_list:
            if common.position_control(asset=coin):
                database.set_islong(asset=coin, isLong=True)
            else:
                database.set_islong(asset=coin, isLong=False)
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
