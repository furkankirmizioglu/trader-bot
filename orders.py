import configparser
import datetime
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from common import tweet
from database import order_log

config = configparser.ConfigParser()
config.read('BinanceBot.properties')
API_KEY = config.get('BinanceSignIn', 'apikey')
API_SECRET_KEY = config.get('BinanceSignIn', 'apisecretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
SUBMIT_ORDER_LOG = "{0} - {3} order for {2} amount of {1} has been successfully submitted."
TWEET_OCO_FORMAT = "{0} - {1} order for {2} has been successfully submitted.\nLimit : {3}\nStop-Limit: {4}"
logging.basicConfig(level=logging.INFO)


# Submit spot limit orders to Binance.
def limit_order(pair, side, quantity, limit_price):
    now = datetime.datetime.now().replace(microsecond=0)
    try:
        client.create_order(symbol=pair,
                            side=side,
                            type=Client.ORDER_TYPE_LIMIT,
                            quantity=quantity,
                            price=limit_price,
                            timeInForce=Client.TIME_IN_FORCE_GTC)
        log = SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper())
        logging.info(log)
    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)


# Submit spot oco orders to Binance.
def oco_order(pair, side, quantity, oco_price, stop, stop_limit):
    now = datetime.datetime.now().replace(microsecond=0)
    try:
        response = client.create_oco_order(symbol=pair,
                                           side=side,
                                           quantity=quantity,
                                           price=oco_price,
                                           stopPrice=stop,
                                           stopLimitPrice=stop_limit,
                                           stopLimitTimeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orders'][0]['orderId']
        log = SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper())
        logging.info(log)
        tweet(TWEET_OCO_FORMAT.format(now, side.capitalize(), pair, oco_price, stop_limit))
        order_log(instance_id=now.strftime("%d/%m/%Y %H:%M:%S"),
                  orderId=orderId,
                  asset=pair,
                  side=side,
                  quantity=quantity,
                  price=oco_price,
                  stop_price=stop_limit)
    except BinanceAPIException as e:
        # error handling goes here
        print(e)
    except BinanceOrderException as e:
        # error handling goes here
        print(e)


# Submit leveraged market orders to Binance.
def market_order(pair, order_side, quantity):
    now = datetime.datetime.now().replace(microsecond=0)
    try:
        client.create_order(symbol=pair,
                            side=order_side,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=quantity)
        log = SUBMIT_ORDER_LOG.format(now, pair, quantity, order_side.upper())
        logging.info(log)

    except BinanceAPIException as e:
        # error handling goes here
        print(e)
    except BinanceOrderException as e:
        # error handling goes here
        print(e)
