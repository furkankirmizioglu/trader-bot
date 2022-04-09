# TRADES ON SPOT MARKET.
# TIME PERIOD IS 1 HOUR
# USES Z SCORE, MAVILIMW AND AVERAGE TRUE RANGE INDICATORS
# TRANSACTIONS WILL BE TWEETED.
import logging
import time
from datetime import datetime
from binance.client import Client
import common
from database import initializer, set_islong, set_order_flag
from coin import Coin
from orders import oco_order

logging.basicConfig(level=logging.INFO)
USDT_AMOUNT = 0
coin_list = ['CRVBUSD', 'DYDXBUSD']


def trader(asset):
    start = time.time()
    coin = Coin(asset=asset)

    # BUY CONDITIONS.
    # If didn't purchase this asset before and buy flag equals 1, then function enters buy conditions.
    if not coin.is_long and coin.buyFlag == 1:

        # If already have a buy order but trend signal has broken, then cancel the order. Else just pass.
        if coin.hasLongOrder:
            if coin.prevPrice < coin.mavilimw and coin.sellFlag == 1:
                common.cancel_order(asset=coin.pair, order_side=Client.SIDE_BUY)
            else:
                pass

        # If previous close price is greater than mavilim price, then enter this condition.
        elif coin.prevPrice > coin.mavilimw:

            # If BUSD amount is less than minimum USD ($12) raise an exception and quit.
            if USDT_AMOUNT < common.MIN_USD:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))

            # Previous close price - ATR for limit buy level.
            limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)

            # If previous close price is greater than mavilim + atr, then enter this condition.
            if coin.prevPrice > (coin.mavilimw + coin.atr):
                # Previous price + (ATR * 49 / 100) for stop trigger.
                stop = common.truncate(coin.prevPrice + (coin.atr * 98 / 100), coin.priceDec)
                # Previous price + (ATR / 2) for stop limit.
                stop_limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)

            else:
                # Mavilim price + (ATR * 98 / 100) for stop trigger.
                stop = common.truncate(coin.mavilimw + (coin.atr * 98 / 100), coin.priceDec)
                # Mavilim price + ATR for stop limit.
                stop_limit = common.truncate(coin.mavilimw + coin.atr, coin.priceDec)

            # The purchase amount is calculated by USDT amount / stop limit price.
            quantity = common.truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

            # Submit order to Binance. Send tweet, write log to ORDER_LOG table and terminal.
            oco_order(pair=coin.pair,
                      side=Client.SIDE_BUY,
                      quantity=quantity,
                      oco_price=limit,
                      stop=stop,
                      stop_limit=stop_limit)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

        # If Z-SCORE is less than -1 and last price is less than bottom level, submit a buy order.
        # However, price will be less than mavilim price. So sets sell flag to 0 for preventing sell order.
        elif coin.zScore < -1 and coin.lastPrice < coin.bottom:
            if USDT_AMOUNT < common.MIN_USD:
                now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                raise Exception(logging.error(common.MIN_AMOUNT_EXCEPTION_LOG.format(now, coin.pair, common.MIN_USD)))

            limit = common.truncate(coin.lastPrice - coin.atr, coin.priceDec)
            stop = common.truncate(coin.lastPrice + (coin.atr * 45 / 100), coin.priceDec)
            stop_limit = common.truncate(coin.lastPrice + coin.atr / 2, coin.priceDec)
            quantity = common.truncate(USDT_AMOUNT / stop_limit, coin.qtyDec)

            oco_order(pair=coin.pair,
                      side=Client.SIDE_BUY,
                      quantity=quantity,
                      oco_price=limit,
                      stop=stop,
                      stop_limit=stop_limit)
            set_order_flag(asset=coin.pair, side=Client.SIDE_SELL, flag=0)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # SELL CONDITIONS.
    # If already purchased the asset and sell flag equals 1, then enter this condition.
    elif coin.is_long and coin.sellFlag == 1:

        # If there is already a sell order but sell signal has broken, then cancel the sell order.
        if coin.hasShortOrder:
            if coin.prevPrice > coin.mavilimw and coin.buyFlag == 1:
                common.cancel_order(asset=coin.pair, order_side=Client.SIDE_SELL)
            else:
                pass

        # If previous close price is less than mavilim price submit a sell order.
        elif coin.prevPrice < coin.mavilimw:

            # Previous close price + ATR value for limit sell level.
            limit = common.truncate(coin.prevPrice + coin.atr, coin.priceDec)

            # If previous close price is less than mavilim + ATR, then enter this condition.
            if coin.prevPrice < (coin.mavilimw - coin.atr):
                # Previous close price - (ATR * 98 / 100) for stop trigger.
                stop = common.truncate(coin.prevPrice - (coin.atr * 98 / 100), coin.priceDec)
                # Previous close price - ATR for stop limit.
                stop_limit = common.truncate(coin.prevPrice - coin.atr, coin.priceDec)
            else:
                # Mavilim price - (ATR * 98 / 100) for stop trigger.
                stop = common.truncate(coin.mavilimw - (coin.atr * 98 / 100), coin.priceDec)
                # Mavilim price - (ATR / 2) for stop limit.
                stop_limit = common.truncate(coin.mavilimw - coin.atr, coin.priceDec)

            # Coin amount information is getting from spot wallet.
            quantity = common.wallet(asset=coin.pair)
            # Submit sell order to Binance. Send tweet, write log to ORDER_LOG table and terminal.
            oco_order(pair=coin.pair,
                      side=Client.SIDE_SELL,
                      quantity=quantity,
                      oco_price=limit,
                      stop=stop,
                      stop_limit=stop_limit)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

        # IF Z-SCORE is greater than 1.5 and last price is greater than top level, then submit a top sell order.
        # However, price will be greater than mavilim price. So it sets buy flag to 0 for preventing buy order.
        elif coin.zScore > 1.5 and coin.lastPrice > coin.top:

            # Last price + ATR for limit sell level.
            limit = common.truncate(coin.lastPrice + coin.atr, coin.priceDec)
            # Last price - (ATR * 45 / 100) for stop trigger level.
            stop = common.truncate(coin.lastPrice - (coin.atr * 45 / 100), coin.priceDec)
            # Last price - (ATR / 2) for stop limit level.
            stop_limit = common.truncate(coin.lastPrice - coin.atr / 2, coin.priceDec)
            # Coin amount information fetching from spot wallet.
            quantity = common.wallet(asset=coin.pair)

            # Submit sell order to Binance. Send tweet, write log to ORDER_LOG table and terminal.
            oco_order(pair=coin.pair,
                      side=Client.SIDE_SELL,
                      quantity=quantity,
                      oco_price=limit,
                      stop=stop,
                      stop_limit=stop_limit)
            set_order_flag(asset=coin.pair, side=Client.SIDE_BUY, flag=0)
            logging.info(common.PROCESS_TIME_LOG.format(common.truncate((time.time() - start), 3)))

    # If previous close price crosses up mavilim and sell flag is 0 then set sell flag to 1.
    if coin.prevPrice > coin.mavilimw and coin.sellFlag == 0:
        set_order_flag(asset=coin.pair, side=Client.SIDE_SELL, flag=1)
    # If previous close price crosses down mavilim and buy flag is 0 then buy flag to 1
    elif coin.prevPrice < coin.mavilimw and coin.buyFlag == 0:
        set_order_flag(asset=coin.pair, side=Client.SIDE_BUY, flag=1)


# MAIN AND INFINITE LOOP FUNCTION.
def bot():
    global coin_list, USDT_AMOUNT
    hasPosList = initializer(pair_list=coin_list)
    if len(hasPosList) > 0:
        logging.info(common.HAVE_ASSET_LOG.format(', '.join(hasPosList)))
    del hasPosList
    while 1:
        while 1:
            for coin in coin_list:
                try:
                    USDT_AMOUNT = common.usd_alloc(coin_list)
                    set_islong(asset=coin, isLong=common.position_control(asset=coin))
                    trader(asset=coin)
                    time.sleep(15)
                except Exception as e:
                    now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
                    print(now + e)
                else:
                    pass


start_now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
common.tweet(common.START_LOG.format(start_now, ", ".join(coin_list)))
logging.info(common.START_LOG.format(start_now, ", ".join(coin_list)))
bot()
