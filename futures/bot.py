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
import common
import constants
import database as database
from orders import marketOrder, stopMarketOrder
from coin import Coin

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
LONG = 'LONG'
SHORT = 'SHORT'
QUANTITY = 'QUANTITY'
PAIRLIST = constants.PAIRLIST
basicConfig(level=INFO)


def FetchUSDT(pairlist):
    restart = True
    while restart:
        try:
            USDT = common.USD_ALLOCATOR(pairlist)
            restart = False
            return USDT
        except Exception as ex:
            error(ex)
            continue


def LongFunction(coin):
    if (coin.prevPrice > coin.mavilimw) or (coin.zScore < -1 and coin.lastPrice < coin.bottom):
        # If user have short position, close this before open a new long position.
        if coin.short:
            try:
                marketOrder(pair=coin.pair,
                            side=SIDE_BUY,
                            quantity=coin.quantity,
                            reduceOnly=True,
                            logPrice=coin.lastPrice)
                database.bulkUpdatePrmOrder(pair=coin.pair,
                                            columns=[SHORT, QUANTITY],
                                            values=(0, 0))
                log = constants.CLOSE_POSITION_LOG.format(common.Now(), coin.pair, SHORT, coin.lastPrice)
                common.tweet(log)
                common.notifier(log)
                info(log)
            except Exception as ex:
                raise ex

        # Open long position.
        try:
            USDT = FetchUSDT(pairlist=PAIRLIST)
            quantity = common.truncate(USDT * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
            # Workaround -> Subtract %5 from quantity for prevent "margin is insufficient" error.
            quantity = common.truncate(quantity - quantity * 0.05, coin.qtyDec)
            marketOrder(pair=coin.pair,
                        side=SIDE_BUY,
                        quantity=quantity,
                        reduceOnly=False,
                        logPrice=coin.lastPrice)
            database.bulkUpdatePrmOrder(pair=coin.pair,
                                        columns=[LONG, QUANTITY],
                                        values=(1, quantity))
            log = constants.FUTURES_MARKET_ORDER_LOG.format(common.Now(), LONG, coin.pair, coin.lastPrice)
            common.notifier(log)
            common.tweet(log)
            info(log)

            if coin.zScore < -1 and coin.lastPrice < coin.bottom:
                stopPrice = common.truncate((coin.lastPrice - coin.lastPrice / 10), coin.priceDec)
                stopMarketOrder(pair=coin.pair,
                                side=SIDE_SELL,
                                stopPrice=stopPrice)
                database.updatePrmOrder(pair=coin.pair,
                                        column='SHORT_HOLD',
                                        value=1)
                log = constants.FUTURES_STOP_ORDER_LOG.format(common.Now(), coin.pair, SHORT, stopPrice)
                common.notifier(log)
                common.tweet(log)
                info(log)

        except Exception as ex:
            raise ex


def ShortFunction(coin):
    if (coin.prevPrice < coin.mavilimw) or (coin.zScore > 1 and coin.lastPrice > coin.top):
        # If user have a long position, close this before open a short one.
        if coin.long:
            try:
                marketOrder(pair=coin.pair,
                            side=SIDE_SELL,
                            quantity=coin.quantity,
                            reduceOnly=True,
                            logPrice=coin.lastPrice)
                database.bulkUpdatePrmOrder(pair=coin.pair, columns=[LONG, QUANTITY], values=(0, 0))
                log = constants.CLOSE_POSITION_LOG.format(common.Now(), coin.pair, LONG, coin.lastPrice)
                common.tweet(log)
                common.notifier(log)
                info(log)
            except Exception as ex:
                raise ex

        # Open short position.
        try:
            USDT = FetchUSDT(pairlist=PAIRLIST)
            quantity = common.truncate(USDT * constants.LEVERAGE / coin.lastPrice, coin.qtyDec)
            # Workaround -> Subtract %5 from quantity for prevent "margin is insufficient" error.
            quantity = common.truncate(quantity - quantity * 0.05, coin.qtyDec)
            marketOrder(pair=coin.pair,
                        side=SIDE_SELL,
                        quantity=quantity,
                        reduceOnly=False,
                        logPrice=coin.lastPrice)
            database.bulkUpdatePrmOrder(pair=coin.pair,
                                        columns=[SHORT, QUANTITY],
                                        values=(1, quantity))
            log = constants.FUTURES_MARKET_ORDER_LOG.format(common.Now(), SHORT, coin.pair, coin.lastPrice)
            common.notifier(log)
            common.tweet(log)
            info(log)

            if coin.zScore > 1 and coin.lastPrice > coin.top:
                stopPrice = common.truncate((coin.lastPrice + coin.lastPrice / 10), coin.priceDec)
                stopMarketOrder(pair=coin.pair,
                                side=SIDE_BUY,
                                stopPrice=stopPrice)
                database.updatePrmOrder(pair=coin.pair,
                                        column='LONG_HOLD',
                                        value=1)
                log = constants.FUTURES_STOP_ORDER_LOG.format(common.Now(), coin.pair, LONG, stopPrice)
                common.notifier(log)
                common.tweet(log)
                info(log)
        except Exception as ex:
            raise ex


def CheckHoldFlags(coin):
    if coin.prevPrice > coin.mavilimw and coin.shortHold:
        database.updatePrmOrder(pair=coin.pair, column='SHORT_HOLD', value=0)
    elif coin.prevPrice < coin.mavilimw and coin.longHold:
        database.updatePrmOrder(pair=coin.pair, column='LONG_HOLD', value=0)


def Trader(coin):
    coin = Coin(pair=coin)
    info(constants.INITIAL_LOG.format(common.Now(), coin.pair, coin.lastPrice, coin.zScore, coin.top, coin.bottom))
    try:
        if not coin.long and not coin.longHold:
            LongFunction(coin=coin)  # LONG CONDITIONS.

        elif not coin.short and not coin.shortHold:
            ShortFunction(coin=coin)  # SHORT CONDITIONS.

        CheckHoldFlags(coin=coin)

    except BinanceAPIException as e:
        if e.code == -1021:  # If exception is about a timestamp issue, ignore it and don't notify that exception.
            pass
        else:
            error(e)
            common.mailSender(traceback.format_exc())


# MAIN AND INFINITE LOOP FUNCTION.
def MultiProcessTrader():
    startTime = perf_counter()
    processes = [multiprocessing.Process(target=Trader, args=[pair]) for pair in PAIRLIST]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    finishTime = perf_counter()
    info(constants.PROCESS_TIME_LOG.format(common.truncate(finishTime - startTime, 2)))
    sleep(10)
    system('clear')


def Bot():
    common.Initializer(PAIRLIST)
    while 1:
        MultiProcessTrader()


if __name__ == '__main__':
    info(constants.START_LOG.format(common.Now(), ", ".join(PAIRLIST)))
    Bot()
