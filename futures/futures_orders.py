import configparser
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from common import tweet
from futures_database import order_log

config = configparser.ConfigParser()
config.read('BinanceBot.properties')
API_KEY = config.get('BinanceSignIn', 'apikey')
API_SECRET_KEY = config.get('BinanceSignIn', 'apisecretkey')
client = Client(api_key=API_KEY, api_secret=API_SECRET_KEY)
SUBMIT_ORDER_LOG = "{0} - {3} order for {2} amount of {1} has been submitted at {} price."
FUTURE_ORDER_TWEET = "{0} - {1} order for {2} has been submitted.\nLimit : {3}\nStop-Limit: {4}"
logging.basicConfig(level=logging.INFO)


def futures_limit_order(now, pair, side, quantity, limit):
    try:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               price=limit,
                                               quantity=quantity,
                                               type=Client.FUTURE_ORDER_TYPE_LIMIT,
                                               timeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = response['orders'][0]['orderId']
        logging.info(SUBMIT_ORDER_LOG.format(now, pair, quantity, side.upper()))
        tweet(FUTURE_ORDER_TWEET.format(now, side.capitalize(), pair, limit))
        order_log(instance_id=now.strftime("%d/%m/%Y %H:%M:%S"),
                  orderId=orderId,
                  asset=pair,
                  side=side,
                  quantity=quantity,
                  price=limit)

    except BinanceAPIException as e:
        # error handling goes here
        print(e)
    except BinanceOrderException as e:
        # error handling goes here
        print(e)
