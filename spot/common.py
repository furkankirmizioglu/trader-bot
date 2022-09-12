from logging import basicConfig, INFO, info
from math import trunc
from datetime import datetime, timedelta
import tweepy
from binance.client import Client
import constants
import database

client = Client(api_key=constants.API_KEY, api_secret=constants.API_SECRET_KEY)
basicConfig(level=INFO)


def Now():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


# Truncates the given value.
def truncate(number, decimals):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return trunc(number)

    factor = 10.0 ** decimals
    return trunc(number * factor) / factor


# Sets decimal values based on selected asset.
def decimal_place(asset):
    symbolInfo = client.get_symbol_info(asset)
    min_price = str(symbolInfo['filters'][0]['minPrice'])
    min_qty = str(symbolInfo['filters'][2]['minQty'])
    start = '0.'
    end = '1'
    truncate_price = len(min_price[min_price.find(start) + len(start):min_price.rfind(end)]) + 1
    if min_qty.startswith('1.00'):
        truncate_qty = 0
    else:
        truncate_qty = len(min_qty[min_qty.find(start) + len(start):min_qty.rfind(end)]) + 1

    return truncate_price, truncate_qty


# Retrieves last 2000 of price movements.
def price_action(symbol, interval):
    first_set = client.get_klines(symbol=symbol, interval=interval, limit=1000)
    timestamp = first_set[0][0]
    timestampsec = datetime.fromtimestamp(timestamp / 1e3) - timedelta(hours=1)
    timestampsec = int(datetime.timestamp(timestampsec))
    exp = len(str(timestamp)) - len(str(timestampsec))
    timestampsec *= pow(10, exp)
    second_set = client.get_klines(symbol=symbol, interval=interval, limit=1000, endTime=timestampsec)
    joined_list = [*second_set, *first_set]
    return joined_list


# Fetches account's balance from Binance wallet.
def wallet(asset):
    if asset != constants.BUSD:
        data = client.get_asset_balance(asset=asset.replace(constants.BUSD, ""))
        return float(data['free']) + float(data['locked'])
    else:
        data = client.get_asset_balance(asset=asset)
        return float(data['free'])


def get_min_qty(asset):
    qty_info = client.get_symbol_info(asset)
    min_qty = float(qty_info['filters'][2]['minQty'])
    return min_qty


# Checks if user has purchased the asset.
def position_control(asset):
    min_qty = database.get_minQty(asset=asset)
    return True if wallet(asset=asset) > min_qty else False


# Checks if an order is already submitted.
def open_order_control(asset, order_side):
    position = client.get_open_orders(symbol=asset)
    if len(position) == 0:
        return False
    elif len(position) > 0:
        for x in position:
            if x['side'] == order_side:
                return True
            else:
                return False


# Cancels given order.
def cancel_order(asset, order_side):
    now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
    orders = client.get_open_orders(symbol=asset)
    order_id = orders[-1]['orderId']
    client.cancel_order(symbol=asset, orderId=order_id)
    log = constants.CANCEL_ORDER_LOG.format(now, asset, order_side.upper())
    info(log)
    tweet(status=log)


# Sets amount of purchasing dynamically.
def USD_ALLOCATOR(pairList):
    priceDec, qtyDec = database.get_decimals(asset=constants.BUSD + constants.USDT)
    divider = 0
    for x in pairList:
        has_asset = database.get_islong(x)
        has_order = database.get_hasBuyOrder(asset=x)
        if not has_asset and not has_order:
            divider += 1
    return truncate(wallet(constants.BUSD) / divider, priceDec) if divider > 0 else truncate(wallet(constants.BUSD),
                                                                                             priceDec)


def initializer(pairList):
    has_long = []
    database.init_data(asset=constants.BUSD + constants.USDT)
    for pair in pairList:
        database.init_data(asset=pair)
        isLong = position_control(asset=pair)
        database.set_islong(asset=pair, isLong=isLong)
        if isLong:
            has_long.append(pair)

        hasBuyOrder = open_order_control(asset=pair, order_side=constants.SIDE_BUY)
        database.set_hasBuyOrder(asset=pair, hasBuyOrder=hasBuyOrder)
        hasSellOrder = open_order_control(asset=pair, order_side=constants.SIDE_SELL)
        database.set_hasSellOrder(asset=pair, hasSellOrder=hasSellOrder)
    return has_long


# Sends tweet.
def tweet(status):
    auth = tweepy.OAuthHandler(constants.TWITTER_API_KEY, constants.TWITTER_API_SECRET_KEY)
    auth.set_access_token(constants.TWITTER_ACCESS_TOKEN, constants.TWITTER_ACCESS_SECRET_TOKEN)
    twitter = tweepy.API(auth)
    twitter.update_status(status)
