# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query


def init_data(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    if len(result) == 0:
        parameter.insert({'asset': asset, 'long': None, 'short': None, 'longHold': None, 'shortHold': None})


def get_long_hold(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['longHold']


def set_long_hold(asset, hold):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'longHold': hold}, query.asset == asset)


def get_short_hold(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['shortHold']


def set_short_hold(asset, hold):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'shortHold': hold}, query.asset == asset)


def get_long(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['long']


def set_long(asset, isLong):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'long': isLong}, query.asset == asset)


def get_short(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['short']


def set_short(asset, isShort):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'short': isShort}, query.asset == asset)


def order_log(instance_id, orderId, asset, side, quantity, price):
    parameter = TinyDB('data/futures_order_log.json')
    parameter.insert({
        'instance_id': instance_id,
        'orderId': orderId,
        'asset': asset,
        'side': side,
        'quantity': quantity,
        'price': price,
    })
