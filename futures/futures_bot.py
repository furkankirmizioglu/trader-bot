# TRADES ON FUTURES MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import traceback
from logging import basicConfig, INFO, info, error
import multiprocessing
from os import system
from time import sleep, perf_counter
from binance.exceptions import BinanceAPIException
import futures_common as common
import futures_constants as constants
import futures_database as database
from futures_orders import marketOrder, stopMarketOrder, TrailingStopOrder
from futures_coin import Coin

PAIRLIST = constants.PAIRLIST
basicConfig(level=INFO)


def fetch_usdt(pairlist):
    restart = True
    while restart:
        try:
            USDT = common.usdt_allocator(pairlist)
            restart = False
            return USDT
        except Exception as ex:
            error(ex)
            continue


# Z-Score -2'den küçük olduğunda ve son fiyat dip değerinin altına düştüğünde çalışacak fonksiyondur.
# Eğer önceden açılmış bir short varsa, trailing stop long emri açılarak short pozisyonun takip edilmesi sağlanır.
# Bu short pozisyon kapanmadan dipten long pozisyon açılmamalı.
def bottom_long(coin):
    if coin.long == 0:
        # Eğer short pozisyon varsa ve trailing stop long emri yoksa, yeni bir trailing stop long emri oluşturulur.
        if coin.short == 1 and coin.trailingStopLongOrderId == 0:
            order_id = TrailingStopOrder(pair=coin.pair,
                                         side=constants.SIDE_BUY,
                                         quantity=coin.quantity,
                                         activationPrice=coin.lastPrice)
            coin.trailingStopLongOrderId = order_id
            database.update_prm_order(pair=coin.pair, column=constants.TRAILING_STOP_LONG_ORDER_ID, value=order_id)
            log = constants.TRAILING_ORDER_LOG(common.now(), constants.LONG, coin.pair, coin.lastPrice)
            common.tweet(log)
            common.notifier(log)
            common.send_order_info_mail(log)
            info(log)
        elif coin.short == 0 and coin.trailingStopLongOrderId == 0:
            # ---------- LONG MARKET ORDER KOD BLOĞU BAŞLANGICI ----------

            USDT = fetch_usdt(pairlist=PAIRLIST)
            quantity = USDT * constants.LEVERAGE / coin.lastPrice
            quantity = common.truncate(quantity - quantity * 0.02, coin.qtyDec)
            marketOrder(pair=coin.pair,
                        side=constants.SIDE_BUY,
                        quantity=quantity,
                        reduceOnly=False,
                        logPrice=coin.lastPrice)
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.LONG, constants.SHORT_HOLD, constants.QUANTITY],
                                           values=(1, 1, quantity))
            log = constants.FUTURES_MARKET_ORDER_LOG.format(common.now(), constants.LONG, coin.pair, coin.lastPrice)
            common.notifier(log)
            common.send_order_info_mail(log)
            common.tweet(log)
            info(log)

            # ---------- LONG MARKET ORDER KOD BLOĞU BİTİŞİ ----------

            # ---------- STOP ORDER KOD BLOĞU BAŞLANGICI ----------

            stop_price = common.truncate((coin.lastPrice - (
                    coin.lastPrice * (constants.STOP_LOSS_PERCENTAGE / constants.LEVERAGE) / 100)), coin.priceDec)
            stopMarketOrder(pair=coin.pair, side=constants.SIDE_SELL, stopPrice=stop_price)
            log = constants.FUTURES_STOP_ORDER_LOG.format(common.now(), coin.pair, constants.SHORT, stop_price)
            common.notifier(log)
            common.send_order_info_mail(log)
            common.tweet(log)
            info(log)

            # ---------- STOP ORDER KOD BLOĞU BİTİŞİ ----------


def trend_short(coin):
    if coin.short == 0 and coin.shortHold == 0 and coin.trailingStopLongOrderId == 0 and coin.trailingStopShortOrderId == 0:
        # Eğer long pozisyon varsa anlık fiyat üzerinden kapatılır.
        if coin.long == 1:
            marketOrder(pair=coin.pair,
                        side=constants.SIDE_SELL,
                        quantity=coin.quantity,
                        reduceOnly=True,
                        logPrice=coin.lastPrice)
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.LONG, constants.QUANTITY],
                                           values=(0, 0))
            log = constants.CLOSE_POSITION_LOG.format(common.now(), coin.pair, constants.LONG, coin.lastPrice)
            common.tweet(log)
            common.notifier(log)
            common.send_order_info_mail(log)
            info(log)

        USDT = fetch_usdt(pairlist=PAIRLIST)
        quantity = common.truncate(USDT * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
        # Workaround -> Subtract %5 from quantity for prevent "margin is insufficient" error.
        quantity = common.truncate(quantity - quantity * 0.02, coin.qtyDec)
        marketOrder(pair=coin.pair,
                    side=constants.SIDE_SELL,
                    quantity=quantity,
                    reduceOnly=False,
                    logPrice=coin.lastPrice)
        database.prm_order_bulk_update(pair=coin.pair,
                                       columns=[constants.SHORT, constants.QUANTITY],
                                       values=(1, quantity))
        log = constants.FUTURES_MARKET_ORDER_LOG.format(common.now(), constants.SHORT, coin.pair, coin.lastPrice)
        common.notifier(log)
        common.send_order_info_mail(log)
        common.tweet(log)
        info(log)


def trend_long(coin):
    if coin.long == 0 and coin.longHold == 0 and coin.trailingStopLongOrderId == 0 and coin.trailingStopShortOrderId == 0:
        # Eğer short pozisyon varsa anlık fiyattan kapatılır.
        if coin.short == 1:
            marketOrder(pair=coin.pair,
                        side=constants.SIDE_BUY,
                        quantity=coin.quantity,
                        reduceOnly=True,
                        logPrice=coin.lastPrice)
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.SHORT, constants.QUANTITY],
                                           values=(0, 0))
            log = constants.CLOSE_POSITION_LOG.format(common.now(), coin.pair, constants.SHORT, coin.lastPrice)
            common.tweet(log)
            common.notifier(log)
            common.send_order_info_mail(log)
            info(log)

        # Eğer long pozisyon yoksa anlık fiyattan yeni long pozisyon açılır.
        USDT = fetch_usdt(pairlist=PAIRLIST)
        quantity = common.truncate(USDT * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
        quantity = common.truncate(quantity - quantity * 0.02, coin.qtyDec)
        marketOrder(pair=coin.pair,
                    side=constants.SIDE_BUY,
                    quantity=quantity,
                    reduceOnly=False,
                    logPrice=coin.lastPrice)
        database.prm_order_bulk_update(pair=coin.pair,
                                       columns=[constants.LONG, constants.QUANTITY],
                                       values=(1, quantity))
        log = constants.FUTURES_MARKET_ORDER_LOG.format(common.now(), constants.LONG, coin.pair, coin.lastPrice)
        common.notifier(log)
        common.send_order_info_mail(log)
        common.tweet(log)
        info(log)


# Z-Score 2'den büyük olduğunda ve son fiyat tepe değerini aştığında çalışacak fonksiyondur.
# Eğer önceden açılmış bir long varsa, trailing stop short emri açılarak long pozisyonun takip edilmesi sağlanır.
# Bu long pozisyon kapanmadan tepeden short pozisyon açılmamalı.

def top_short(coin):
    if coin.short == 0:
        if coin.long == 1 and coin.trailingStopShortOrderId == 0:
            # Eğer long pozisyon taşıyorsa ve trailing stop order yoksa yeni trailing stop short order açılır.
            order_id = TrailingStopOrder(pair=coin.pair,
                                         side=constants.SIDE_SELL,
                                         quantity=coin.quantity,
                                         activationPrice=coin.lastPrice)
            database.update_prm_order(pair=coin.pair,
                                      column=constants.TRAILING_STOP_SHORT_ORDER_ID,
                                      value=order_id)
            coin.trailingStopShortOrderId = order_id
            log = constants.TRAILING_ORDER_LOG(common.now(), constants.SHORT, coin.pair, coin.lastPrice)
            common.tweet(log)
            common.notifier(log)
            common.send_order_info_mail(log)
            info(log)
        # Eğer artık long pozisyon taşınmıyorsa ve trailing order kapandıysa short pozisyon açılır ve stop değeri belirlenir.
        elif coin.long == 0 and coin.trailingStopShortOrderId == 0:

            # ---------- SHORT MARKET ORDER KOD BLOĞU BAŞLANGICI ----------
            USDT = fetch_usdt(pairlist=PAIRLIST)
            quantity = common.truncate(USDT * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
            quantity = common.truncate(quantity - quantity * 0.02, coin.qtyDec)
            marketOrder(pair=coin.pair,
                        side=constants.SIDE_SELL,
                        quantity=quantity,
                        reduceOnly=False,
                        logPrice=coin.lastPrice)
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.SHORT, constants.LONG_HOLD, constants.QUANTITY],
                                           values=(1, 1, quantity))
            log = constants.FUTURES_MARKET_ORDER_LOG.format(common.now(), constants.SHORT, coin.pair, coin.lastPrice)
            common.notifier(log)
            common.send_order_info_mail(log)
            common.tweet(log)
            info(log)

            # ---------- SHORT MARKET ORDER KOD BLOĞU BİTİŞİ ----------

            # ---------- STOP ORDER KOD BLOĞU BAŞLANGICI ----------

            stop_price = common.truncate((coin.lastPrice + (
                    coin.lastPrice * (constants.STOP_LOSS_PERCENTAGE / constants.LEVERAGE) / 100)), coin.priceDec)
            stopMarketOrder(pair=coin.pair,
                            side=constants.SIDE_BUY,
                            stopPrice=stop_price)
            log = constants.FUTURES_STOP_ORDER_LOG.format(common.now(), coin.pair, constants.LONG, stop_price)
            common.notifier(log)
            common.send_order_info_mail(log)
            common.tweet(log)
            info(log)

            # ---------- STOP ORDER KOD BLOĞU BİTİŞİ ----------


def check_hold_flags(coin):
    if coin.prevPrice > coin.mavilimw and coin.shortHold == 1:
        database.update_prm_order(pair=coin.pair, column=constants.SHORT_HOLD, value=0)

    elif coin.prevPrice < coin.mavilimw and coin.longHold == 1:
        database.update_prm_order(pair=coin.pair, column=constants.LONG_HOLD, value=0)


def check_trailing_order_status(coin):
    if coin.trailingStopLongOrderId != 0:
        status = common.check_order_status(pair=coin.pair, order_id=coin.trailingStopLongOrderId)
        if status == 'FILLED':
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.SHORT, constants.TRAILING_STOP_LONG_ORDER_ID,
                                                    constants.QUANTITY],
                                           values=(0, 0, 0))
            coin.short = 0
            coin.trailingStopLongOrderId = 0
            coin.quantity = 0
            bottom_long(coin=coin)
    elif coin.trailingStopShortOrderId != 0:
        status = common.check_order_status(pair=coin.pair, order_id=coin.trailingStopShortOrderId)
        if status == 'FILLED':
            database.prm_order_bulk_update(pair=coin.pair,
                                           columns=[constants.LONG, constants.TRAILING_STOP_SHORT_ORDER_ID,
                                                    constants.QUANTITY],
                                           values=(0, 0, 0))
            coin.long = 0
            coin.trailingStopShortOrderId = 0
            coin.quantity = 0
            top_short(coin=coin)


def trader(coin):
    coin = Coin(pair=coin)
    info(constants.INITIAL_LOG.format(common.now(), coin.pair, coin.lastPrice, coin.zScore, coin.top, coin.bottom))
    try:
        if coin.prevPrice > coin.mavilimw:
            if coin.zScore > 2 and coin.lastPrice > coin.top:
                top_short(coin=coin)
            else:
                trend_long(coin=coin)
        elif coin.prevPrice < coin.mavilimw:
            if coin.zScore < -2 and coin.lastPrice < coin.bottom:
                bottom_long(coin=coin)
            else:
                trend_short(coin=coin)

        check_hold_flags(coin=coin)
        check_trailing_order_status(coin=coin)

    except BinanceAPIException as e:
        if e.code != -1021:  # If exception is about a timestamp issue, ignore it and don't notify that exception.
            error(e)
            common.send_mail(traceback.format_exc())
    except Exception as ex:
        error(ex)
        common.send_mail(traceback.format_exc())


# MAIN AND INFINITE LOOP FUNCTION.
def multi_process_trader():
    start_time = perf_counter()
    processes = [multiprocessing.Process(target=trader, args=[pair]) for pair in PAIRLIST]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    finish_time = perf_counter()
    info(constants.PROCESS_TIME_LOG.format(common.truncate(finish_time - start_time, 2)))
    sleep(10)
    system('clear')


def bot():
    common.initializer(PAIRLIST)
    while 1:
        multi_process_trader()


if __name__ == '__main__':
    info(constants.START_LOG.format(common.now(), ", ".join(PAIRLIST)))
    bot()
