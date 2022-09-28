# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query
import common
import os

path = os.path.dirname(__file__)
order_param_path = path + "/data/order_param.json"
order_log_path = path + "/data/order_log.json"


def initDB(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    if len(result) == 0:
        priceDec, qtyDec = common.decimal_place(asset=asset)
        minQty = common.getMinimumQuantity(asset=asset)
        parameter.insert(
            {'asset': asset,
             'isLong': None,
             'buy': 1,
             'sell': 1,
             'priceDec': priceDec,
             'qtyDec': qtyDec,
             'minQty': minQty,
             'hasBuyOrder': None,
             'hasSellOrder': None
             })


def getLatestOrder(pair):
    parameter = TinyDB(order_log_path)
    query = Query()
    result = parameter.search(query.asset == pair)
    return result[-1]['orderId']


def removeOrderLog(orderId):
    parameter = TinyDB(order_log_path)
    query = Query()
    parameter.remove(query.orderId == orderId)


def getHasBuyOrder(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['hasBuyOrder']


def getHasSellOrder(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['hasSellOrder']


def setHasBuyOrder(asset, hasBuyOrder):
    parameter = TinyDB(order_param_path)
    query = Query()
    parameter.update({'hasBuyOrder': hasBuyOrder}, query.asset == asset)


def setHasSellOrder(asset, hasSellOrder):
    parameter = TinyDB(order_param_path)
    query = Query()
    parameter.update({'hasSellOrder': hasSellOrder}, query.asset == asset)


def getMinimumQuantity(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['minQty']


def getDecimalValues(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['priceDec'], result[0]['qtyDec']


def getHoldFlags(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['buy'], result[0]['sell']


def setOrderFlag(asset, side, flag):
    parameter = TinyDB(order_param_path)
    query = Query()
    if side == 'BUY':
        parameter.update({'buy': flag}, query.asset == asset)
    elif side == 'SELL':
        parameter.update({'sell': flag}, query.asset == asset)


def getIsLong(asset):
    parameter = TinyDB(order_param_path)
    query = Query()
    response = parameter.search(query.asset == asset)
    return response[0]['isLong'] if len(response) > 0 else None


def setIsLong(asset, isLong):
    parameter = TinyDB(order_param_path)
    query = Query()
    parameter.update({'isLong': isLong}, query.asset == asset)


def insertOrderLog(instance_id, orderId, asset, side, quantity, price, stop_price):
    parameter = TinyDB(order_log_path)
    parameter.insert({
        'instance_id': instance_id,
        'orderId': orderId,
        'asset': asset,
        'side': side,
        'quantity': quantity,
        'price': price,
        'stop_price': stop_price
    })
