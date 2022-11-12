import configparser
import os

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)

START_LOG = "{0} - TraderBot Futures has started. Running for {1}"
LONG_POSITION_LOG = "You already hold long position on these assets: {0}"
SHORT_POSITION_LOG = "You already hold short position on these assets: {0}"
CANCEL_ORDER_LOG = "{0} - Latest futures {2} order of {1} has cancelled."
PROCESS_TIME_LOG = "This cycle has processed in {} seconds."

INITIAL_LOG = "{0} - {1} | Price: {2} | Z-Score: {3} | Top: {4} | Bottom: {5}"
CLOSE_POSITION_LOG = "{0} - Your {1} {2} position has closed at {3} market price."
FUTURES_LIMIT_ORDER_LOG = "{0} - Futures {1} order for {2} has submitted.\nTake-Profit : {4}\nStop-Limit : {3}"
FUTURES_MARKET_ORDER_LOG = "{0} - Futures {1} order for {2} has submitted at {3} market price."
FUTURES_STOP_ORDER_LOG = "{0} - Futures stop {1} order for {2} has submitted at {3}."
TRAILING_ORDER_LOG = "{0} - Futures trailing stop {1} order for {2} has submitted.\nActivation Price : {3}"

NOTIFIER_TITLE = "You have a new trade activity !"

USDT = 'USDT'

BINANCE_FUTURES_API_KEY = config.get('BinanceFutures', 'apikey')
BINANCE_FUTURES_API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')

TWITTER_API_KEY = config.get('TwitterAPI', 'consumer_key')
TWITTER_API_SECRET_KEY = config.get('TwitterAPI', 'consumer_secret_key')
TWITTER_ACCESS_TOKEN = config.get('TwitterAPI', 'access_token')
TWITTER_ACCESS_SECRET_TOKEN = config.get('TwitterAPI', 'access_secret_token')

SENDER_EMAIL = config.get('Gmail', 'sender_email')
EMAIL_PASSWORD = config.get('Gmail', 'emailpassword')
RECEIVER_EMAIL = config.get('Gmail', 'receiver_email')

EMAIL_FORMAT = 'Subject: {}\n\n{}'
EMAIL_SUBJECT = "TraderBot Futures - An Exception Occurred!"

FIREBASE_DEVICE_KEY = config.get('FirebaseAPI', 'device_key')

PAIRLIST = config.get('TraderBotFuturesConfig', 'pairList').split(',')
PRICE_INTERVAL = config.get('TraderBotFuturesConfig', 'interval')
LEVERAGE = config.getint("TraderBotFuturesConfig", "LEVERAGE")
STOP_LOSS_PERCENTAGE = config.getint("TraderBotFuturesConfig", "STOP_LOSS_PERCENTAGE")
TEST_MODE = config.getboolean("TraderBotFuturesConfig", "TEST_MODE")
