import os
from logging import basicConfig, INFO, info
import math
from datetime import datetime, timedelta
from smtplib import SMTP
import tweepy
from binance.client import Client, BinanceAPIException
from firebase_admin import messaging, credentials, initialize_app
import futures_database as database
import futures_constants as constants

client = Client(api_key=constants.BINANCE_FUTURES_API_KEY, api_secret=constants.BINANCE_FUTURES_API_SECRET_KEY)

path = os.path.dirname(__file__)
firebase = path + "/data/firebase.json"
firebase_cred = credentials.Certificate(firebase)
firebase_app = initialize_app(firebase_cred)
basicConfig(level=INFO)


def now():
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
def price_actions(pair, interval):
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
def check_open_orders(pair, order_side):
    position = client.futures_get_open_orders(symbol=pair)
    if len(position) == 0:
        return False
    elif len(position) > 0:
        for x in position:
            if x['side'] == order_side:
                return x['orderId']
            else:
                return 0


def send_mail(exceptionMessage):
    try:
        smtpConn = SMTP('smtp.gmail.com', 587)
        smtpConn.starttls()
        smtpConn.login(constants.SENDER_EMAIL, constants.EMAIL_PASSWORD)
        exceptionMessage = constants.EMAIL_FORMAT.format(constants.EMAIL_SUBJECT, exceptionMessage)
        smtpConn.sendmail(constants.SENDER_EMAIL, constants.RECEIVER_EMAIL, exceptionMessage)
        smtpConn.quit()
    except Exception as ex:
        info(ex)


def initializer(pairList):
    database.create_prm_order()
    database.create_order_log()
    for pair in pairList:
        try:
            client.futures_change_margin_type(symbol=pair, marginType='ISOLATED')
        except BinanceAPIException as e:
            if e.code != -4046 and e.code != -1021:
                raise e
        try:
            client.futures_change_position_mode(dualSidePosition='false')
        except BinanceAPIException as e:
            if e.code != -4059 and e.code != -1021:
                raise e
        try:
            client.futures_change_leverage(symbol=pair, leverage=constants.LEVERAGE)
        except BinanceAPIException as e:
            if e.code != -1021:
                raise e

        data = database.select_prm_order(pair=pair)
        if len(data) == 0:
            priceDec, qtyDec, minQty = decimal_place(pair=pair)
            long, short, quantity = check_position(pair)
            database.insert_prm_order((pair, priceDec, qtyDec, minQty, long, short, quantity, 0, 0, 0, 0))
        else:
            long, short, quantity = check_position(pair)
            columns = [constants.LONG, constants.SHORT, constants.QUANTITY]
            database.prm_order_bulk_update(pair=pair, columns=columns, values=(long, short, quantity))

    info("Database update has completed successfully.")


# Checks if user has either long or short position and returns amount.
def check_position(pair):
    positionInfo = client.futures_position_information(symbol=pair)
    positionAmt = float(positionInfo[-1]['positionAmt'])
    if positionAmt > 0:
        return 1, 0, positionAmt
    elif positionAmt < 0:
        return 0, 1, abs(positionAmt)
    else:
        return 0, 0, 0


def usdt_balance():
    balance = client.futures_account_balance()
    for x in balance:
        if x['asset'] == constants.USDT:
            return float(x['withdrawAvailable'])


# Sets amount of purchasing dynamically.
def usdt_allocator(asset_list):
    divider = 0
    for x in asset_list:
        query = database.select_prm_order(pair=x)[-1]
        isLong = query[4]
        isShort = query[5]
        if not isLong and not isShort:
            divider += 1
    return usdt_balance() / divider if divider > 0 else usdt_balance()


def check_order_status(pair, order_id):
    response = client.futures_get_order(symbol=pair, orderId=order_id)
    return response['status']


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
    if constants.NOTIFIER:
        messaging.send(message)
