import configparser
import logging
import os
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import constants
from common import tweet
from database import order_log

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)
API_KEY = config.get('BinanceFutures', 'apikey')
API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
logging.basicConfig(level=logging.INFO)


def limitOrder(now, pair, side, quantity, limit):
    try:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               price=limit,
                                               quantity=quantity,
                                               type=Client.FUTURE_ORDER_TYPE_LIMIT,
                                               timeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orderId']
        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper(), limit))
        tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, side.capitalize(), pair, limit))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=quantity, price=limit)

    except BinanceAPIException as e:
        logging.error(e)
    except BinanceOrderException as e:
        logging.error(e)


def marketOrder(now, pair, side, quantity, logPrice):
    try:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               quantity=quantity,
                                               type=Client.FUTURE_ORDER_TYPE_MARKET,
                                               timeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orderId']
        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper(), logPrice))
        tweet(constants.FUTURE_MARKET_ORDER_TWEET.format(now, side.capitalize(), pair, logPrice))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=quantity, price=logPrice)

    except BinanceAPIException as e:
        logging.error(e)
    except BinanceOrderException as e:
        logging.error(e)


def stopMarketOrder(now, pair, side, stopPrice):
    try:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               type=Client.FUTURE_ORDER_TYPE_STOP_MARKET,
                                               closePosition='true',
                                               stopPrice=stopPrice)
        orderId = response['orderId']
        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, 0, side.upper(), stopPrice))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=0, price=stopPrice)
    except BinanceAPIException as e:
        logging.error(e)
    except BinanceOrderException as e:
        logging.error(e)


def takeProfitMarketOrder(now, pair, side, stopPrice):
    try:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               type=Client.FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                                               closePosition='true',
                                               stopPrice=stopPrice)
        orderId = response['orderId']
        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, 0, side.upper(), stopPrice))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=0, price=stopPrice)
    except BinanceAPIException as e:
        logging.error(e)
    except BinanceOrderException as e:
        logging.error(e)
