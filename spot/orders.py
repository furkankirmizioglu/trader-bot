from logging import basicConfig, INFO, info
from binance.client import Client
import constants
from common import tweet, Now, notifier
from database import insertIntoOrderLog

client = Client(api_key=constants.API_KEY, api_secret=constants.API_SECRET_KEY)
basicConfig(level=INFO)

TEST_MODE = constants.TEST_MODE


# Submit spot limit orders to Binance.
def stopLimitOrder(pair, side, quantity, limit, stopTrigger):
    now = Now()
    if not TEST_MODE:
        stopLimitResponse = client.create_order(symbol=pair,
                                                side=side,
                                                type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                                                quantity=quantity,
                                                price=limit,
                                                stopPrice=stopTrigger,
                                                timeInForce=Client.TIME_IN_FORCE_GTC)

        orderId = stopLimitResponse['orderId']
        orderLogParameters = (orderId, now, pair, side, quantity, limit, stopTrigger)
        insertIntoOrderLog(orderLogParameters)

    log = constants.STOP_LIMIT_ORDER_LOG.format(now, pair, side.upper(), limit)
    info(log)
    tweet(log)
    notifier(constants.NOTIFIER_STOP_LIMIT_ORDER_LOG.format(side.capitalize(), pair, limit))


# Submit spot oco orders to Binance.
def oco_order(pair, side, quantity, limit, stop, stop_limit):
    now = Now()
    if not TEST_MODE:
        ocoResponse = client.create_oco_order(symbol=pair,
                                              side=side,
                                              quantity=quantity,
                                              price=limit,
                                              stopPrice=stop,
                                              stopLimitPrice=stop_limit,
                                              stopLimitTimeInForce=Client.TIME_IN_FORCE_GTC)
        orderId = ocoResponse['orders'][0]['orderId']

        orderLogParameters = (orderId, now, pair, side, quantity, limit, stop_limit)
        insertIntoOrderLog(orderLogParameters)
    log = constants.OCO_ORDER_LOG.format(now, side.upper(), pair, limit, stop_limit)
    info(log)
    tweet(log)
    notifier(constants.NOTIFIER_OCO_ORDER_LOG.format(side.capitalize(), pair, limit, stop_limit))
