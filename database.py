# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query
import common


def init_data(asset, isLong):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    priceDec, qtyDec = common.decimal_place(asset=asset)
    buy = 0 if isLong else 1
    sell = 1 if isLong else 0
    if len(result) == 0:
        parameter.insert(
            {'asset': asset, 'isLong': isLong, 'buy': buy, 'sell': sell, 'priceDec': priceDec, 'qtyDec': qtyDec})


def get_decimals(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['priceDec'], result[0]['qtyDec']


def get_order_flag(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['buy'], result[0]['sell']


def set_order_flag(asset, side, flag):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    if side == 'BUY':
        parameter.update({'buy': flag}, query.asset == asset)
    elif side == 'SELL':
        parameter.update({'sell': flag}, query.asset == asset)


def get_islong(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['isLong'] if len(response) > 0 else None


def set_islong(asset, isLong):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    parameter.update({'isLong': isLong}, query.asset == asset)


def order_log(instance_id, orderId, asset, side, quantity, price, stop_price):
    parameter = TinyDB('data/order_log.json')
    parameter.insert({
        'instance_id': instance_id,
        'orderId': orderId,
        'asset': asset,
        'side': side,
        'quantity': quantity,
        'price': price,
        'stop_price': stop_price
    })


def initializer(pair_list):
    has_long = []
    init_data(asset='BUSDUSDT', isLong=None)
    for coin in pair_list:
        isLong = common.position_control(asset=coin)
        init_data(asset=coin, isLong=isLong)
        if isLong:
            has_long.append(coin)
    return has_long
