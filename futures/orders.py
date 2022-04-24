import configparser
import logging
import os
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from common import tweet
from database import order_log

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)
API_KEY = config.get('BinanceFutures', 'apikey')
API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
SUBMIT_ORDER_LOG = "{0} - {3} order for {2} amount of {1} has been submitted at {4} price."
FUTURE_LIMIT_ORDER_TWEET = "{0} - {1} order for {2} has been submitted.\nLimit : {3}"
FUTURE_MARKET_ORDER_TWEET = "{0} - {1} order for {2} has been submitted at market price.\nMarket : {3}"
logging.basicConfig(level=logging.INFO)


def limit_order(pair, side, quantity, limit):
    try:
        now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               price=limit,
                                               quantity=quantity,
                                               type=Client.FUTURE_ORDER_TYPE_LIMIT,
                                               timeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orderId']
        logging.info(SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper(), limit))
        tweet(FUTURE_LIMIT_ORDER_TWEET.format(now, side.capitalize(), pair, limit))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=quantity, price=limit)

    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)


def market_order(pair, side, quantity, logPrice):
    try:
        now = datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               type=Client.FUTURE_ORDER_TYPE_MARKET,
                                               quantity=quantity)
        orderId = response['orderId']
        logging.info(SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper(), logPrice))
        tweet(FUTURE_MARKET_ORDER_TWEET.format(now, side.capitalize(), pair, quantity))
        order_log(instance_id=now, orderId=orderId, asset=pair, side=side, quantity=quantity, price=logPrice)
    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)
