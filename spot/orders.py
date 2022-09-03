import configparser
import datetime
import logging
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from common import tweet
from database import order_log

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBot.ini"
config.read(dirName)
API_KEY = config.get('BinanceSignIn', 'apikey')
API_SECRET_KEY = config.get('BinanceSignIn', 'secretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
LIMIT_ORDER_LOG = "{0} - {3} order for {2} amount of {1} has submitted.\nLimit : {4}"
OCO_ORDER_LOG = "{0} - {1} order for {2} has submitted.\nLimit : {3} | Stop-Limit: {4}"
logging.basicConfig(level=logging.INFO)


# Submit spot limit orders to Binance.
def limit_order(pair, side, quantity, limit_price):
    now = datetime.datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
    try:
        client.create_order(symbol=pair,
                            side=side,
                            type=Client.ORDER_TYPE_LIMIT,
                            quantity=quantity,
                            price=limit_price,
                            timeInForce=Client.TIME_IN_FORCE_GTC)
        log = LIMIT_ORDER_LOG.format(now, pair, quantity, side.upper(), limit_price)
        logging.info(log)
    except (BinanceAPIException, BinanceOrderException) as ex:
        raise ex


# Submit spot oco orders to Binance.
def oco_order(pair, side, quantity, limit, stop, stop_limit):
    now = datetime.datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S")
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
        logging.info(log)
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
