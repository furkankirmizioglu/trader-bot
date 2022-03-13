import configparser
import logging
import math
from datetime import datetime, timedelta
import tweepy
from binance.client import Client
import futures_database as database

BUSD = 'BUSD'
USDT = 'USDT'
OPEN_ORDER_LOG = "{0} - You already have a {2} order of {1}."
HAVE_ASSET_LOG = "You already purchased these assets: {0}"
MIN_USD = 12
MIN_AMOUNT_EXCEPTION_LOG = "{0} - Buy amount cannot be less than {2} USDT! {1} buy order is invalid and won't submit."
START_LOG = "{0} - TraderBot has started. Running for {1}"
CANCEL_ORDER_LOG = "{0} - Latest {2} order of {1} has been cancelled."
PROCESS_TIME_LOG = "This order has been processed in {} seconds."
UP = 'UP'
DOWN = 'DOWN'
config = configparser.ConfigParser()
config.read('BinanceBot.properties')
API_KEY = config.get('BinanceFutures', 'fapikey')
API_SECRET_KEY = config.get('BinanceFutures', 'fapisecretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
logging.basicConfig(level=logging.INFO)


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
    info = client.get_symbol_info(asset)
    min_price = str(info['filters'][0]['minPrice'])
    min_qty = str(info['filters'][2]['minQty'])
    start = '0.'
    end = '1'
    truncate_price = len(min_price[min_price.find(start) + len(start):min_price.rfind(end)]) + 1
    if min_qty.startswith('1.00'):
        truncate_qty = 0
    else:
        truncate_qty = len(min_qty[min_qty.find(start) + len(start):min_qty.rfind(end)]) + 1

    return truncate_price, truncate_qty


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
            if x['positionSide'] == order_side:
                return True
            else:
                return False


def initializer(pair_list):
    has_long = []
    for coin in pair_list:
        database.init_data(asset=coin)
        if position_control(asset=coin, position_side="LONG"):
            database.set_long(asset=coin, isLong=True)
            has_long.append(coin)
        elif position_control(asset=coin, position_side="SHORT"):
            database.set_short(asset=coin, isShort=True)
            has_long.append(coin)
        else:
            database.set_long(asset=coin, isLong=False)
            database.set_short(asset=coin, isShort=False)
    return has_long


# Checks if user has a position.
def position_control(asset, position_side):
    info = client.futures_position_information(symbol=asset)
    if float(info[-1]['positionAmt']) > 0:
        return True if info[-1]['positionSide'] == position_side else False
    else:
        return False


def wallet(asset):
    balance = client.futures_account_balance()
    for x in balance:
        if x['asset'] == asset:
            return float(x['withdrawAvailable'])


# Sets amount of purchasing dynamically.
def usd_alloc(asset_list):
    divider = 0
    for x in asset_list:
        isLong = database.get_long(x)
        isShort = database.get_short(x)
        has_long_order = open_order_control(asset=x, order_side="LONG")
        has_short_order = open_order_control(asset=x, order_side="SHORT")
        if not isLong and not isShort and not has_long_order and not has_short_order:
            divider += 1
    return wallet(asset=BUSD) / divider if divider > 0 else wallet(asset=BUSD)
