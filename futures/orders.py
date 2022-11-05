import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import constants
from common import tweet, Now
from database import insertIntoOrderLog

client = Client(api_key=constants.BINANCE_FUTURES_API_KEY, api_secret=constants.BINANCE_FUTURES_API_SECRET_KEY)
logging.basicConfig(level=logging.INFO)
TEST_MODE = constants.TEST_MODE


def limitOrder(pair, side, quantity, limit):
    now = Now()
    try:
        if not TEST_MODE:
            response = client.futures_create_order(symbol=pair,
                                                   side=side,
                                                   price=limit,
                                                   quantity=quantity,
                                                   type=Client.FUTURE_ORDER_TYPE_LIMIT,
                                                   timeInForce=Client.TIME_IN_FORCE_GTC)
            orderLogParameters = (response['orderId'], now, pair, side, quantity, limit)
            insertIntoOrderLog(orderLogParameters)
            tweet(constants.FUTURE_LIMIT_ORDER_TWEET.format(now, side.capitalize(), pair, limit))

        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, side.upper(), limit))

    except BinanceAPIException as e:
        logging.error(e)
    except BinanceOrderException as e:
        logging.error(e)


def marketOrder(pair, side, quantity, reduceOnly, logPrice):
    now = Now()
    if not TEST_MODE:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               quantity=quantity,
                                               reduceOnly=reduceOnly,
                                               type=Client.FUTURE_ORDER_TYPE_MARKET)
        orderLogParameters = (response['orderId'], now, pair, side, quantity, logPrice)
        insertIntoOrderLog(orderLogParameters)
        tweet(constants.FUTURE_MARKET_ORDER_TWEET.format(now, side.capitalize(), pair, logPrice))

    logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, side.upper(), logPrice))


def stopMarketOrder(pair, side, stopPrice):
    now = Now()
    if not TEST_MODE:
        response = client.futures_create_order(symbol=pair,
                                               side=side,
                                               type=Client.FUTURE_ORDER_TYPE_STOP_MARKET,
                                               closePosition='true',
                                               stopPrice=stopPrice)
        orderLogParameters = (response['orderId'], now, pair, side, 0, 0)
        logging.info(constants.SUBMIT_ORDER_LOG.format(now, pair, side.upper(), stopPrice))
        insertIntoOrderLog(orderLogParameters)


def TrailingStopOrder(pair, side, quantity, activationPrice):
    now = Now()
    if not TEST_MODE:
        tsoResponse = client.create_order(symbol=pair,
                                          side=side,
                                          quantity=quantity,
                                          type=Client.FUTURE_ORDER_TYPE_TAKE_PROFIT,
                                          price=activationPrice,
                                          trailingDelta=300,
                                          timeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = tsoResponse['orderId']
        orderLogParameters = (orderId, now, pair, side, quantity, activationPrice, 0)
        insertIntoOrderLog(orderLogParameters)

    log = constants.TRAILING_ORDER_LOG.format(now, side.upper(), pair, activationPrice)
    logging.info(log)
    tweet(log)

    # notifier(constants.NOTIFIER_TRAILING_ORDER_LOG.format(side.capitalize(), pair, activationPrice))
