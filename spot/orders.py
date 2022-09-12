from logging import basicConfig, INFO, info
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from constants import API_KEY, API_SECRET_KEY, STOP_LIMIT_ORDER_LOG, OCO_ORDER_LOG
from common import tweet, Now
from database import order_log

client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
basicConfig(level=INFO)


# Submit spot limit orders to Binance.
def stop_limit_order(pair, side, quantity, limit, stopLimit):
    try:
        now = Now()
        response = client.create_order(symbol=pair,
                                       side=side,
                                       type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                                       quantity=quantity,
                                       price=limit,
                                       stopPrice=stopLimit,
                                       timeInForce=Client.TIME_IN_FORCE_GTC)
        log = STOP_LIMIT_ORDER_LOG.format(now, pair, side.upper(), limit)
        orderId = response['orderId']
        info(log)
        tweet(log)
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=quantity, price=limit,
                  stop_price=stopLimit)
    except (BinanceAPIException, BinanceOrderException) as ex:
        raise ex


# Submit spot oco orders to Binance.
def oco_order(pair, side, quantity, limit, stop, stop_limit):
    now = Now()
    try:
        response = client.create_oco_order(symbol=pair,
                                           side=side,
                                           quantity=quantity,
                                           price=limit,
                                           stopPrice=stop,
                                           stopLimitPrice=stop_limit,
                                           stopLimitTimeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orders'][0]['orderId']
        log = OCO_ORDER_LOG.format(now, side.upper(), pair, limit, stop_limit)
        info(log)
        tweet(log)
        order_log(instance_id=now,
                  orderId=orderId,
                  asset=pair,
                  side=side,
                  quantity=quantity,
                  price=limit,
                  stop_price=stop_limit)
    except (BinanceAPIException, BinanceOrderException) as ex:
        raise ex
