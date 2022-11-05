from logging import info
import math
from datetime import datetime, timedelta
from smtplib import SMTP
from unittest import TestCase

import tweepy
from binance.client import Client, BinanceAPIException
from firebase_admin import messaging

import database as database
import constants

client = Client(api_key=constants.BINANCE_FUTURES_API_KEY, api_secret=constants.BINANCE_FUTURES_API_SECRET_KEY)


def Now():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


# Truncates the given value.
def truncate(number, decimals):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


# Sets decimal values based on selected asset.
def decimal_place(pair):
    decimalInfo = client.futures_exchange_info()
    decimalInfo = decimalInfo['symbols']
    for x in decimalInfo:
        if x['pair'] == pair:
            minPrice = str(x['filters'][0]['tickSize'])
            minQty = str(x['filters'][1]['minQty'])
            start = '0.'
            end = '1'
            priceDec = len(minPrice[minPrice.find(start) + len(start):minPrice.rfind(end)]) + 1
            if minQty.startswith(end):
                qtyDec = 0
            else:
                qtyDec = len(minQty[minQty.find(start) + len(start):minQty.rfind(end)]) + 1
            return priceDec, qtyDec, minQty


# Retrieves last 2000 price actions.
def priceActions(pair, interval):
    first_set = client.futures_klines(symbol=pair, interval=interval, limit=1000)
    timestamp = first_set[0][0]
    second_timestamp = datetime.fromtimestamp(timestamp / 1e3) - timedelta(hours=1)
    second_timestamp = int(datetime.timestamp(second_timestamp))
    exp = len(str(timestamp)) - len(str(second_timestamp))
    second_timestamp *= pow(10, exp)
    second_set = client.futures_klines(symbol=pair, interval=interval, limit=1000, endTime=second_timestamp)
    joined_list = [*second_set, *first_set]
    return joined_list


# Checks if an order is already submitted.
def checkOpenOrder(pair, order_side):
    position = client.futures_get_open_orders(symbol=pair)
    if len(position) == 0:
        return False
    elif len(position) > 0:
        for x in position:
            if x['side'] == order_side:
                return 1
            else:
                return 0


def mailSender(exceptionMessage):
    try:
        smtpConn = SMTP('smtp.gmail.com', 587)
        smtpConn.starttls()
        smtpConn.login(constants.SENDER_EMAIL, constants.EMAIL_PASSWORD)
        exceptionMessage = constants.EMAIL_FORMAT.format(constants.EMAIL_SUBJECT, exceptionMessage)
        smtpConn.sendmail(constants.SENDER_EMAIL, constants.RECEIVER_EMAIL, exceptionMessage)
        smtpConn.quit()
    except Exception as ex:
        info(ex)
        pass


def Initializer(pairList):
    for pair in pairList:
        try:
            client.futures_change_margin_type(symbol=pair, marginType='ISOLATED')
        except BinanceAPIException as e:
            if e.code == -4046:
                pass
            else:
                raise e
        try:
            client.futures_change_position_mode(dualSidePosition='false')
        except BinanceAPIException as e:
            if e.code == -4059:
                pass
            else:
                raise e
        try:
            client.futures_change_leverage(symbol=pair, leverage=constants.LEVERAGE)
        except BinanceAPIException as e:
            raise e

        data = database.selectAllFromPrmOrder(pair=pair)
        if len(data) == 0:
            priceDec, qtyDec, minQty = decimal_place(pair=pair)
            long, short, quantity = checkPosition(pair)
            hasLongOrder = checkOpenOrder(pair=pair, order_side='LONG')
            hasShortOrder = checkOpenOrder(pair=pair, order_side='SHORT')
            parameters = (pair, priceDec, qtyDec, minQty, long, short, quantity, 0, 0, hasLongOrder, hasShortOrder)
            database.initPrmOrderTable(parameters)
        else:
            long, short, quantity = checkPosition(pair)
            hasLongOrder = checkOpenOrder(pair=pair, order_side='LONG')
            hasShortOrder = checkOpenOrder(pair=pair, order_side='SHORT')
            values = (long, short, quantity, hasLongOrder, hasShortOrder)
            columns = ['LONG', 'SHORT', 'QUANTITY', 'HAS_LONG_ORDER', 'HAS_SHORT_ORDER']
            database.bulkUpdatePrmOrder(pair=pair, columns=columns, values=values)

    info("Database update has completed successfully.")


# Checks if user has either long or short position and returns amount.
def checkPosition(pair):
    positionInfo = client.futures_position_information(symbol=pair)
    positionAmt = float(positionInfo[-1]['positionAmt'])
    if positionAmt > 0:
        return True, False, positionAmt
    elif positionAmt < 0:
        return False, True, positionAmt
    else:
        return False, False, 0


def USDTBALANCE():
    balance = client.futures_account_balance()
    for x in balance:
        if x['asset'] == constants.USDT:
            return float(x['withdrawAvailable'])


# Sets amount of purchasing dynamically.
def USD_ALLOCATOR(asset_list):
    divider = 0
    for x in asset_list:
        isLong = database.getLong(pair=x)
        isShort = database.getShort(pair=x)
        if not isLong and not isShort:
            divider += 1
    return USDTBALANCE() / divider if divider > 0 else USDTBALANCE()


# Sends tweet.
def tweet(status):
    auth = tweepy.OAuthHandler(constants.TWITTER_API_KEY, constants.TWITTER_API_SECRET_KEY)
    auth.set_access_token(constants.TWITTER_ACCESS_TOKEN, constants.TWITTER_ACCESS_SECRET_TOKEN)
    twitter = tweepy.API(auth)
    twitter.update_status(status)


def notifier(logText):
    # See documentation on defining a message payload.
    notification = messaging.Notification(
        title=constants.NOTIFIER_TITLE,
        body=logText
    )
    message = messaging.Message(
        token=constants.FIREBASE_DEVICE_KEY,
        notification=notification
    )
    # Send a message to the device corresponding to the provided
    # registration token.
    messaging.send(message)


class Test(TestCase):
    def test_check_position(self):
        assert checkPosition(pair="LRCUSDT") == (False, True, -79)
