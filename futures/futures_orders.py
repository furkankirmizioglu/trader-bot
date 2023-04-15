from binance.client import Client
from futures_constants import BINANCE_FUTURES_API_KEY, BINANCE_FUTURES_API_SECRET_KEY, TEST_MODE
from futures_common import now
from futures_database import insert_order_log

client = Client(api_key=BINANCE_FUTURES_API_KEY, api_secret=BINANCE_FUTURES_API_SECRET_KEY)
TEST_MODE = TEST_MODE


def limitOrder(pair, side, quantity, limit):
    if not TEST_MODE:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               price=limit,
                                               quantity=quantity,
                                               type=Client.FUTURE_ORDER_TYPE_LIMIT,
                                               timeInForce=Client.TIME_IN_FORCE_GTC)
        insert_order_log((response['orderId'], now(), pair, side, quantity, limit))


def marketOrder(pair, side, quantity, reduceOnly, logPrice):
    if not TEST_MODE:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               quantity=quantity,
                                               reduceOnly=reduceOnly,
                                               type=Client.FUTURE_ORDER_TYPE_MARKET)
        insert_order_log((response['orderId'], now(), pair, side.upper(), quantity, logPrice))


def stopMarketOrder(pair, side, stopPrice):
    if not TEST_MODE:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               type=Client.FUTURE_ORDER_TYPE_STOP_MARKET,
                                               closePosition='true',
                                               stopPrice=stopPrice)
        insert_order_log((response['orderId'], now(), pair, side.upper(), 0, 0))


def TrailingStopOrder(pair, side, quantity, activationPrice):
    if not TEST_MODE:
        tsoResponse = client.futures_create_order(symbol=pair,
                                                  side=side,
                                                  quantity=quantity,
                                                  type='TRAILING_STOP_MARKET',
                                                  price=activationPrice,
                                                  callbackRate=2,
                                                  timeInForce=Client.TIME_IN_FORCE_GTC)
        insert_order_log((tsoResponse['orderId'], now(), pair, side.upper(), quantity, activationPrice))
        return tsoResponse['orderId']
    else:
        return 11111111111
