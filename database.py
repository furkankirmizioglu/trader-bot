# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query


def init_data(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    if len(result) == 0:
        parameter.insert({'asset': asset, 'isLong': None, 'buy': -1, 'sell': -1})


def init_order_flag(asset, isLong):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    if result[-1]['buy'] == -1:
        buy = 0 if isLong else 1
        sell = 1 if isLong else 0
        parameter.update({'buy': buy, 'sell': sell}, query.asset == asset)


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
