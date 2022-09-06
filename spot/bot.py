# TRADES ON SPOT MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import configparser
import logging
import time
import os
from datetime import datetime
import common
import database
from coin import Coin
from orders import oco_order, limit_order

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBot.ini"
config.read(dirName)
pairList = config.get("TraderBotConfig", "pairlist").split(',')
TEST_MODE = config.get('TraderBotConfig', 'testMode')
PRICE_INTERVAL = config.get("TraderBotConfig", "interval")
INITIAL_LOG = "{0} - {1} | Price: {2} | Z-Score: {3} | Top: {4} | Bottom: {5}"
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'


def fetchUSDT(pairlist):
    restart = True
    while restart:
        try:
            USDT = common.usd_alloc(pairlist)
            restart = False
            return USDT
        except Exception as ex:
            logging.error(ex)
            continue


def checkFlag(coin):
    # If previous close price crosses up mavilim and sell flag is 0 then set sell flag to 1.
    if coin.prevPrice > coin.mavilimw and coin.sellFlag == 0:
        database.set_order_flag(asset=coin.pair, side=SIDE_SELL, flag=1)
    # If previous close price crosses down mavilim and buy flag is 0 then buy flag to 1
    elif coin.prevPrice < coin.mavilimw and coin.buyFlag == 0:
        database.set_order_flag(asset=coin.pair, side=SIDE_BUY, flag=1)


def trader(asset, USDT_AMOUNT):
    start = time.time()

    coin = Coin(asset=asset, interval=PRICE_INTERVAL)
    now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
    logging.info(INITIAL_LOG.format(now, coin.pair, coin.lastPrice, coin.zScore, coin.top, coin.bottom))

    # BUY CONDITIONS.
    # If didn't purchase this asset before and buy flag equals 1, then enter this condition.
    if not coin.is_long and coin.buyFlag == 1:

        # If there is already a buy order but buy condition has disappeared, the buy order will be canceled.
        if coin.hasBuyOrder:
            if coin.prevPrice < coin.mavilimw:
                common.cancel_order(asset=coin.pair, order_side=SIDE_BUY)
                database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=False)
            else:
                pass

        # This condition will be entered if previous close price is above of mavilim value,
        elif coin.prevPrice > coin.mavilimw:

            # If BUSD amount is less than minimum value ($12) raise an exception and quit.
            if USDT_AMOUNT < common.MIN_USD:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))

            # Previous close price - ATR for limit buy price.
            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Previous close price + (ATR * 90 / 100) for trigger.
            stop = common.truncate(coin.prevPrice + (coin.atr * 90 / 100), coin.priceDec)
            # Previous close price + ATR for stop limit.
            stop_limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)
            # Quantity would calculate with USDT / stop limit price.
            quantity = common.truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

            try:
                # Submits order to Binance. Sends tweet, writes the order log both ORDER_LOG table and terminal.
                oco_order(pair=coin.pair, side=SIDE_BUY, quantity=quantity, limit=limit, stop=stop,
                          stop_limit=stop_limit)
                database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=True)
                logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))
            except Exception as ex:
                logging.error(ex)

        # If Z-SCORE is less than -1 and last price is below bottom level, submit a buy order.
        # However, price would below mavilim value. That's why it would set sell flag to 0 for prevent wrong sell order.
        elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
            if USDT_AMOUNT < common.MIN_USD:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))

            # Last price - ATR for limit buy price.
            limit = common.truncate(coin.lastPrice - coin.atr, coin.priceDec)
            # Last price + (ATR * 45 / 100) for trigger.
            stop = common.truncate(coin.lastPrice + (coin.atr * 45 / 100), coin.priceDec)
            # Last price + (ATR / 2) for stop-limit price.
            stop_limit = common.truncate(coin.lastPrice + coin.atr / 2, coin.priceDec)
            # Quantity information would calculate with USDT / stop-limit price.
            quantity = common.truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

            # Submits order to Binance. Sends tweet, writes the order log both ORDER_LOG table and terminal.
            try:
                oco_order(pair=coin.pair,
                          side=SIDE_BUY,
                          quantity=quantity,
                          limit=limit,
                          stop=stop,
                          stop_limit=stop_limit)
                database.set_hasBuyOrder(asset=coin.pair, hasBuyOrder=True)
                database.set_order_flag(asset=coin.pair, side=SIDE_SELL, flag=0)
                logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))
            except Exception as ex:
                logging.error(ex)

    # SELL CONDITIONS.
    # If already purchased the asset and sell flag equals 1, then enter this condition.
    if coin.is_long and coin.sellFlag == 1:

        # If there is already a sell order but sell condition has disappeared, cancel the sell order.
        if coin.hasSellOrder:
            if coin.prevPrice > coin.mavilimw:
                common.cancel_order(asset=coin.pair, order_side=SIDE_SELL)
                database.set_hasSellOrder(asset=coin.pair, hasSellOrder=False)
            else:
                pass

        # If previous close price would below of mavilim price, submit a limit sell order.
        elif coin.prevPrice < coin.mavilimw:

            # Previous close price - ATR for stop limit.
            stop_limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            # Quantity information would fetch from spot wallet.
            quantity = common.truncate(common.wallet(asset=coin.pair), coin.qtyDec)

            # Submits limit sell order to Binance. Sends tweet, writes log both ORDER_LOG table and terminal.
            try:
                limit_order(pair=coin.pair, side=SIDE_SELL, quantity=quantity, limit=stop_limit)
                database.set_hasSellOrder(asset=coin.pair, hasSellOrder=True)
                logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))
            except Exception as ex:
                logging.error(ex)

        # When Z-SCORE would greater than 1 and last price would above of top level, it'll submit a top-level sell order.
        # However, price would be above of mavilim value. That's why it would set buy flag to 0 for prevent wrong buy order.
        elif coin.zScore > 1 and coin.lastPrice > coin.top:

            # Last price + ATR for limit sell level.
            limit = common.truncate(coin.lastPrice + coin.atr, coin.priceDec)
            # Last price - (ATR * 45 / 100) for stop trigger level.
            stop = common.truncate(coin.lastPrice - (coin.atr * 45 / 100), coin.priceDec)
            # Last price - (ATR / 2) for stop limit level.
            stop_limit = common.truncate(coin.lastPrice - coin.atr / 2, coin.priceDec)
            # Quantity information would fetch from spot wallet.
            quantity = common.wallet(asset=coin.pair)

            # Submit sell order to Binance. Sends tweet, writes log both ORDER_LOG table and terminal.
            try:
                oco_order(pair=coin.pair, side=SIDE_SELL, quantity=quantity, limit=limit, stop=stop,
                          stop_limit=stop_limit)
                database.set_hasSellOrder(asset=coin.pair, hasSellOrder=True)
                database.set_order_flag(asset=coin.pair, side=SIDE_BUY, flag=0)
                logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))
            except Exception as ex:
                logging.error(ex)

    checkFlag(coin=coin)


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global pairList
    hasPosList = common.initializer(pair_list=pairList)
    if len(hasPosList) > 0:
        logging.info(common.HAVE_ASSET_LOG.format(', '.join(hasPosList)))
    del hasPosList
    while 1:
        USDT = fetchUSDT(pairlist=pairList)
        for pair in pairList:
            try:
                trader(asset=pair, USDT_AMOUNT=USDT)
                time.sleep(10)
            except Exception as ex:
                logging.error(ex)
            else:
                pass
        # Clears console after each cycle.
        os.system('clear')


start_now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
log = common.START_LOG.format(start_now, ", ".join(pairList))
if not TEST_MODE:
    common.tweet(log)
logging.info(log)
bot()
