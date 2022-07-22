# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query
import common as common


def createDatabase(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    if len(result) == 0:
        priceDec, qtyDec = common.decimal_place(asset=asset)
        parameter.insert(
            {'asset': asset,
             'pricePrecision': priceDec,
             'quantityPrecision': qtyDec,
             'long': None,
             'short': None,
             'quantity': 0,
             'longHold': False,
             'shortHold': False,
             'hasLongOrder': None,
             'hasShortOrder': None})
    else:
        pass


def getLongHold(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['longHold']


def setLongHold(asset, hold):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'longHold': hold}, query.asset == asset)


def getShortHold(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['shortHold']


def setShortHold(asset, hold):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'shortHold': hold}, query.asset == asset)


def getLong(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['long']


def setLong(asset, isLong):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'long': isLong}, query.asset == asset)


def getShort(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['short']


def setShort(asset, isShort):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'short': isShort}, query.asset == asset)


def getHasLongOrder(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['hasLongOrder']


def setHasLongOrder(asset, hasLongOrder):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'hasLongOrder': hasLongOrder}, query.asset == asset)


def getHasShortOrder(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['hasShortOrder']


def setHasShortOrder(asset, hasShortOrder):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'hasShortOrder': hasShortOrder}, query.asset == asset)


def getQuantity(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['quantity']


def setQuantity(asset, quantity):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    parameter.update({'quantity': quantity}, query.asset == asset)


def getPrecision(asset):
    parameter = TinyDB('data/futures_order_param.json')
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['pricePrecision'], response[0]['quantityPrecision']


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
