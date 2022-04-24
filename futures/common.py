import logging
import math
from datetime import datetime, timedelta
import tweepy
from binance.client import Client, BinanceAPIException
import database as database
import constants

client = Client(api_key=constants.BINANCE_FUTURES_API_KEY, api_secret=constants.BINANCE_FUTURES_API_SECRET_KEY)
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
    info = client.futures_exchange_info()
    info = info['symbols']
    for x in info:
        if x['pair'] == asset:
            minPrice = str(x['filters'][0]['tickSize'])
            minQty = str(x['filters'][1]['minQty'])
            start = '0.'
            end = '1'
            priceDec = len(minPrice[minPrice.find(start) + len(start):minPrice.rfind(end)]) + 1
            if minQty.startswith(end):
                qtyDec = 0
            else:
                qtyDec = len(minQty[minQty.find(start) + len(start):minQty.rfind(end)]) + 1
            return priceDec, qtyDec


# Retrieves last 2000 price actions.
def price_action(symbol, interval):
    first_set = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    timestamp = first_set[0][0]
    second_timestamp = datetime.fromtimestamp(timestamp / 1e3) - timedelta(hours=1)
    second_timestamp = int(datetime.timestamp(second_timestamp))
    exp = len(str(timestamp)) - len(str(second_timestamp))
    second_timestamp *= pow(10, exp)
    second_set = client.futures_klines(symbol=symbol, interval=interval, limit=1000, endTime=second_timestamp)
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

        try:
            client.futures_change_position_mode(dualSidePosition='false')
        except BinanceAPIException as e:
            logging.info(e.message)
            pass

        client.futures_change_leverage(symbol=coin, leverage=constants.LEVERAGE)

        database.createDatabase(asset=coin)
        longPosition, shortPosition, quantity = check_position(asset=coin)

        if longPosition:
            database.setLong(asset=coin, isLong=True)
            database.setQuantity(asset=coin, quantity=quantity)
            has_long.append(coin)
        elif not longPosition:
            database.setLong(asset=coin, isLong=False)
            database.setQuantity(asset=coin, quantity=0)

        if shortPosition:
            database.setShort(asset=coin, isShort=True)
            database.setQuantity(asset=coin, quantity=quantity)
            has_short.append(coin)
        elif not shortPosition:
            database.setQuantity(asset=coin, quantity=0)
            database.setShort(asset=coin, isShort=False)

        hasLongOrder = open_order_control(asset=coin, order_side='BUY')
        database.setHasLongOrder(asset=coin, hasLongOrder=hasLongOrder)

        hasShortOrder = open_order_control(asset=coin, order_side='SELL')
        database.setHasShortOrder(asset=coin, hasShortOrder=hasShortOrder)

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
        isLong = database.getLong(asset=x)
        isShort = database.getShort(asset=x)
        has_long_order = database.getHasLongOrder(asset=x)
        has_short_order = database.getHasShortOrder(asset=x)
        if not isLong and not isShort and not has_long_order and not has_short_order:
            divider += 2
    return wallet(asset=constants.USDT) / divider if divider > 0 else wallet(asset=constants.USDT)


# Sends tweet.
def tweet(status):
    auth = tweepy.OAuthHandler(constants.TWITTER_API_KEY, constants.TWITTER_API_SECRET_KEY)
    auth.set_access_token(constants.TWITTER_ACCESS_TOKEN, constants.TWITTER_ACCESS_SECRET_TOKEN)
    twitter = tweepy.API(auth)
    twitter.update_status(status)
