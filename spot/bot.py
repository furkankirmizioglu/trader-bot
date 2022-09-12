# TRADES ON SPOT MARKET.
# TIME PERIOD IS 2 HOURS
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
from logging import info, error, basicConfig, INFO
from time import time, sleep
from os import system
from common import truncate, tweet, cancel_order, initializer, wallet, USD_ALLOCATOR, Now
import constants
import database
from coin import Coin
from orders import oco_order, stop_limit_order

TEST_MODE = constants.TEST_MODE

basicConfig(level=INFO)


def FetchUSDT(pairlist):
    restart = True
    while restart:
        try:
            USDT = USD_ALLOCATOR(pairlist)
            restart = False
            return USDT
        except Exception as ex:
            error(ex)
            continue


def BuyFunction(coin, start):
    # If there is already a buy order but buy condition has disappeared, the buy order will be canceled.
    if coin.hasBuyOrder:
        if coin.prevPrice < coin.mavilimw and coin.sellFlag == 1:
            cancel_order(asset=coin.pair, order_side=constants.SIDE_BUY)
            database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=False)
        else:
            pass

    # This condition will be entered if previous close price is above of mavilim value,
    elif coin.prevPrice > coin.mavilimw:
        TrendBuyOrder(coin, start)

    # If Z-SCORE is less than -1 and last price is below bottom level, submit a buy order.
    # However, price would below mavilim value. That's why it would set sell flag to 0 for prevent wrong sell order.
    elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
        BottomBuyOrder(coin, start)


def TrendBuyOrder(coin, start):
    USDT_AMOUNT = FetchUSDT(constants.PAIRLIST)

    # If BUSD amount is less than minimum value ($12) raise an exception and quit.
    if USDT_AMOUNT < constants.MIN_USD:
        raise Exception(
            error(constants.MIN_AMOUNT_EXCEPTION_LOG.format(Now(), coin.pair, constants.MIN_USD)))

    # Previous close price - ATR for limit buy price.
    limit = truncate(coin.prevPrice - coin.atr, coin.priceDec)
    # Previous close price + (ATR * 90 / 100) for trigger.
    stop = truncate(coin.prevPrice + (coin.atr * 90 / 100), coin.priceDec)
    # Previous close price + ATR for stop limit.
    stop_limit = truncate(coin.prevPrice + coin.atr, coin.priceDec)
    # Quantity would calculate with USDT / stop limit price.
    quantity = truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

    if not TEST_MODE:
        try:
            # Submits order to Binance. Sends tweet, writes the order log both ORDER_LOG table and terminal.
            oco_order(pair=coin.pair, side=constants.SIDE_BUY, quantity=quantity, limit=limit, stop=stop,
                      stop_limit=stop_limit)
            database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=True)
            info(constants.PROCESS_TIME_LOG.format(truncate((time() - start), 3)))
        except Exception as ex:
            error(ex)


def BottomBuyOrder(coin, start):
    USDT_AMOUNT = FetchUSDT(constants.PAIRLIST)

    if USDT_AMOUNT < constants.MIN_USD:
        raise Exception(
            error(constants.MIN_AMOUNT_EXCEPTION_LOG.format(Now(), coin.pair, constants.MIN_USD)))

    # Last price - ATR for limit buy price.
    limit = truncate(coin.lastPrice - coin.atr, coin.priceDec)
    # Last price + (ATR * 45 / 100) for trigger.
    stop = truncate(coin.lastPrice + (coin.atr * 45 / 100), coin.priceDec)
    # Last price + (ATR / 2) for stop-limit price.
    stop_limit = truncate(coin.lastPrice + coin.atr / 2, coin.priceDec)
    # Quantity information would calculate with USDT / stop-limit price.
    quantity = truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

    # Submits order to Binance. Sends tweet, writes the order log both ORDER_LOG table and terminal.
    if not TEST_MODE:
        try:
            oco_order(pair=coin.pair,
                      side=constants.SIDE_BUY,
                      quantity=quantity,
                      limit=limit,
                      stop=stop,
                      stop_limit=stop_limit)
            database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=True)
            database.set_order_flag(asset=coin.pair, side=constants.SIDE_SELL, flag=0)
            info(constants.PROCESS_TIME_LOG.format(truncate((time() - start), 3)))
        except Exception as ex:
            error(ex)


def SellFunction(coin, start):
    # If there is already a sell order but sell condition has disappeared, cancel the sell order.
    if coin.hasSellOrder:
        if coin.prevPrice > coin.mavilimw and coin.buyFlag == 1:
            cancel_order(asset=coin.pair, order_side=constants.SIDE_SELL)
            database.set_hasSellOrder(asset=coin.pair, hasSellOrder=False)
        else:
            pass

    # If previous close price would below of mavilim price, submit a limit sell order.
    elif coin.prevPrice < coin.mavilimw:

        TrendSellOrder(coin, start)

    # When Z-SCORE would greater than 1 and last price would above of top level, it'll submit a top-level sell order.
    # However, price would be above of mavilim value. That's why it would set buy flag to 0 for prevent wrong buy order.
    elif coin.zScore > 1 and coin.lastPrice > coin.top:

        TopSellOrder(coin, start)


def TrendSellOrder(coin, start):
    # Previous close price - ATR for stop limit.
    stopLimit = truncate(coin.prevPrice - (coin.atr * 90 / 100), coin.priceDec)
    # Previous price + (ATR / 2) for stop limit.
    limit = truncate(coin.prevPrice - coin.atr, coin.priceDec)
    # Quantity information would fetch from spot wallet.
    quantity = truncate(wallet(asset=coin.pair), coin.qtyDec)

    if not TEST_MODE:
        # Submits limit sell order to Binance. Sends tweet, writes log both ORDER_LOG table and terminal.
        try:
            stop_limit_order(pair=coin.pair, side=constants.SIDE_SELL, quantity=quantity, limit=limit, stopLimit=stopLimit)
            database.set_hasSellOrder(asset=coin.pair, hasSellOrder=True)
            info(constants.PROCESS_TIME_LOG.format(truncate((time() - start), 3)))
        except Exception as ex:
            error(ex)


def TopSellOrder(coin, start):
    # Last price + ATR for limit sell level.
    limit = truncate(coin.lastPrice + coin.atr, coin.priceDec)
    # Last price - (ATR * 45 / 100) for stop trigger level.
    stop = truncate(coin.lastPrice - (coin.atr * 45 / 100), coin.priceDec)
    # Last price - (ATR / 2) for stop limit level.
    stop_limit = truncate(coin.lastPrice - coin.atr / 2, coin.priceDec)
    # Quantity information would fetch from spot wallet.
    quantity = wallet(asset=coin.pair)

    if not TEST_MODE:
        # Submit sell order to Binance. Sends tweet, writes log both ORDER_LOG table and terminal.
        try:
            oco_order(pair=coin.pair, side=constants.SIDE_SELL, quantity=quantity, limit=limit, stop=stop,
                      stop_limit=stop_limit)
            database.set_hasSellOrder(asset=coin.pair, hasSellOrder=True)
            database.set_order_flag(asset=coin.pair, side=constants.SIDE_BUY, flag=0)
            info(constants.PROCESS_TIME_LOG.format(truncate((time() - start), 3)))
        except Exception as ex:
            error(ex)


def CheckHoldFlags(coin):
    # If previous close price crosses up mavilim and sell flag is 0 then set sell flag to 1.
    if coin.prevPrice > coin.mavilimw and coin.sellFlag == 0:
        database.set_order_flag(asset=coin.pair, side=constants.SIDE_SELL, flag=1)
    # If previous close price crosses down mavilim and buy flag is 0 then buy flag to 1
    elif coin.prevPrice < coin.mavilimw and coin.buyFlag == 0:
        database.set_order_flag(asset=coin.pair, side=constants.SIDE_BUY, flag=1)


def Trader(pair):
    start = time()
    coin = Coin(pair=pair)
    info(constants.INITIAL_LOG.format(Now(), coin.pair, coin.lastPrice, coin.zScore, coin.top, coin.bottom))

    # BUY CONDITIONS.
    # If didn't purchase the asset before and buy flag equals 1, then enter this condition.
    if not coin.is_long and coin.buyFlag == 1:
        BuyFunction(coin=coin, start=start)

    # SELL CONDITIONS.
    # If already purchased the asset and sell flag equals 1, then enter this condition.
    if coin.is_long and coin.sellFlag == 1:
        SellFunction(coin=coin, start=start)

    CheckHoldFlags(coin=coin)


# MAIN AND INFINITE LOOP FUNCTION.
def Bot():
    hasPosList = initializer(constants.PAIRLIST)
    if len(hasPosList) > 0:
        info(constants.HAVE_ASSET_LOG.format(', '.join(hasPosList)))
    del hasPosList
    while 1:
        for pair in constants.PAIRLIST:
            try:
                Trader(pair=pair)
                sleep(10)
            except Exception as ex:
                error(ex)
            else:
                pass
        # Clears console after each cycle.
        system('clear')


log = constants.START_LOG.format(Now(), ", ".join(constants.PAIRLIST))
info(log)
Bot()
