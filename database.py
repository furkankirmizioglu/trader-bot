# THIS PYTHON SCRIPT
# CONTAINS DATABASE FUNCTIONS
from tinydb import TinyDB, Query
import common


def init_data(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    if len(result) == 0:
        priceDec, qtyDec = common.decimal_place(asset=asset)
        minQty = common.get_min_qty(asset=asset)
        parameter.insert(
            {'asset': asset,
             'isLong': None,
             'buy': 1,
             'sell': 1,
             'priceDec': priceDec,
             'qtyDec': qtyDec,
             'minQty': minQty,
             'hasBuyOrder': common.open_order_control(asset=asset, order_side='BUY'),
             'hasSellOrder': common.open_order_control(asset=asset, order_side='SELL')
             })
    else:
        parameter.update({
            'hasBuyOrder': common.open_order_control(asset=asset, order_side='BUY'),
            'hasSellOrder': common.open_order_control(asset=asset, order_side='SELL')}, query.asset == asset)


def get_hasBuyOrder(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['hasBuyOrder']


def get_min_qty(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['minQty']


def get_hasSellOrder(asset):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    result = parameter.search(query.asset == asset)
    return result[0]['hasSellOrder']


def set_hasBuyOrder(asset, hasBuyOrder):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    parameter.update({'hasBuyOrder': hasBuyOrder}, query.asset == asset)


def set_hasSellOrder(asset, hasSellOrder):
    parameter = TinyDB('data/order_param.json')
    query = Query()
    parameter.update({'hasSellOrder': hasSellOrder}, query.asset == asset)


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
    init_data(asset='BUSDUSDT')
    for coin in pair_list:
        init_data(asset=coin)
        isLong = common.position_control(asset=coin)
        if isLong:
            set_islong(asset=coin, isLong=True)
            has_long.append(coin)
        else:
            set_islong(asset=coin, isLong=False)
    return has_long
