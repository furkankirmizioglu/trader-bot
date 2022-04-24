import configparser
import logging
import math
import os
from datetime import datetime, timedelta
import tweepy
from binance.client import Client, BinanceAPIException
import database as database

USDT = 'USDT'
OPEN_ORDER_LOG = "{0} - You already have a {2} order of {1}."
LONG_POSITION_LOG = "You already carrying long position on these assets: {0}"
SHORT_POSITION_LOG = "You already carrying short position on these assets: {0}"
MIN_USD = 12
MIN_AMOUNT_EXCEPTION_LOG = "{0} - Buy amount cannot be less than {2} USDT! {1} buy order is invalid and won't submit."
START_LOG = "{0} - TraderBot Futures has started. Running for {1}"
CANCEL_ORDER_LOG = "{0} - Latest {2} order of {1} has been cancelled."
PROCESS_TIME_LOG = "This order has been processed in {} seconds."
UP = 'UP'
DOWN = 'DOWN'
config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)
API_KEY = config.get('BinanceFutures', 'apikey')
API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
logging.basicConfig(level=logging.INFO)
LEVERAGE = 5


# Truncates the given value.
def truncate(number, decimals):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


# Sets decimal values based on selected asset.
def decimal_place(asset):
    info = client.futures_exchange_info()
    info = info['symbols']
    for x in info:
        if x['pair'] == asset:
            priceDec = x['pricePrecision']
            qtyDec = x['quantityPrecision']
            return priceDec, qtyDec


# Retrieves last 2000 price actions.
def price_action(symbol, interval):
    first_set = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    timestamp = first_set[0][0]
    timestampsec = datetime.fromtimestamp(timestamp / 1e3) - timedelta(hours=1)
    timestampsec = int(datetime.timestamp(timestampsec))
    exp = len(str(timestamp)) - len(str(timestampsec))
    timestampsec *= pow(10, exp)
    second_set = client.futures_klines(symbol=symbol, interval=interval, limit=1000, endTime=timestampsec)
    joined_list = [*second_set, *first_set]
    return joined_list


# Checks if an order is already submitted.
def open_order_control(asset, order_side):
    position = client.futures_get_open_orders(symbol=asset)
    if len(position) == 0:
        return False
    elif len(position) > 0:
        for x in position:
            if x['side'] == order_side:
                return True
            else:
                return False


def initializer(pair_list):
    has_long = []
    has_short = []
    for coin in pair_list:
        try:
            client.futures_change_margin_type(symbol=coin, marginType='ISOLATED')
        except BinanceAPIException as e:
            logging.info(e.message)
            pass

        client.futures_change_leverage(symbol=coin, leverage=LEVERAGE)

        database.init_data(asset=coin)
        longPosition, shortPosition, quantity = check_position(asset=coin)

        if longPosition:
            database.set_long(asset=coin, isLong=True)
            database.set_quantity(asset=coin, quantity=quantity)
            has_long.append(coin)
        elif not longPosition:
            database.set_long(asset=coin, isLong=False)
            database.set_quantity(asset=coin, quantity=0)

        if shortPosition:
            database.set_short(asset=coin, isShort=True)
            database.set_quantity(asset=coin, quantity=quantity)
            has_short.append(coin)
        elif not shortPosition:
            database.set_quantity(asset=coin, quantity=0)
            database.set_short(asset=coin, isShort=False)

        hasLongOrder = open_order_control(asset=coin, order_side='BUY')
        database.set_hasLongOrder(asset=coin, hasLongOrder=hasLongOrder)

        hasShortOrder = open_order_control(asset=coin, order_side='SELL')
        database.set_hasShortOrder(asset=coin, hasShortOrder=hasShortOrder)

        return has_long, has_short


# Checks if user has position.
def check_position(asset):
    info = client.futures_position_information(symbol=asset)
    positionAmt = float(info[-1]['positionAmt'])
    if positionAmt > 0:
        return True, False, positionAmt
    elif positionAmt < 0:
        return False, True, positionAmt
    else:
        return False, False, 0


def wallet(asset):
    balance = client.futures_account_balance()
    for x in balance:
        if x['asset'] == asset:
            return float(x['withdrawAvailable'])


# Sets amount of purchasing dynamically.
def usd_alloc(asset_list):
    divider = 0
    for x in asset_list:
        isLong = database.get_long(asset=x)
        isShort = database.get_short(asset=x)
        has_long_order = database.get_hasLongOrder(asset=x)
        has_short_order = database.get_hasShortOrder(asset=x)
        if not isLong and not isShort and not has_long_order and not has_short_order:
            divider += 1
    return wallet(asset=USDT) / divider if divider > 0 else wallet(asset=USDT)


# Sends tweet.
def tweet(status):
    auth = tweepy.OAuthHandler(config.get('TwitterAPI', 'consumer_key'),
                               config.get('TwitterAPI', 'consumer_secret_key'))
    auth.set_access_token(config.get('TwitterAPI', 'access_token'), config.get('TwitterAPI', 'access_secret_token'))
    twitter = tweepy.API(auth)
    twitter.update_status(status)
