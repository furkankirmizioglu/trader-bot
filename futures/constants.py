import configparser
import os

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)

START_LOG = "{0} - TraderBot Futures has started. Running for {1}"
LONG_POSITION_LOG = "You already hold long position on these assets: {0}"
SHORT_POSITION_LOG = "You already hold short position on these assets: {0}"
CANCEL_ORDER_LOG = "{0} - Latest futures {2} order of {1} has cancelled."
PROCESS_TIME_LOG = "This order has processed in {} seconds."
INITIAL_LOG = "{0} - {1} | Price: {2} | Z-Score: {3} | Top: {4} | Bottom: {5}"
SUBMIT_ORDER_LOG = "{0} - Futures {2} order for {1} has been submitted at {3} price."
FUTURE_LIMIT_ORDER_TWEET = "{0} - Futures {1} order for {2} has been submitted.\nTake-Profit : {4}\nStop-Limit : {3}"
FUTURE_MARKET_ORDER_TWEET = "{0} - Futures {1} order for {2} has submitted at {3} market price."
CLOSE_POSITION_LOG = "{0} - Your {1} {2} position has closed at {3} market price."
TRAILING_ORDER_LOG = "{0} - trailing stop {1} order for {2} has submitted.\nActivation Price : {3}"

LEVERAGE = 10
USDT = 'USDT'

BINANCE_FUTURES_API_KEY = config.get('BinanceFutures', 'apikey')
BINANCE_FUTURES_API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')

TWITTER_API_KEY = config.get('TwitterAPI', 'consumer_key')
TWITTER_API_SECRET_KEY = config.get('TwitterAPI', 'consumer_secret_key')
TWITTER_ACCESS_TOKEN = config.get('TwitterAPI', 'access_token')
TWITTER_ACCESS_SECRET_TOKEN = config.get('TwitterAPI', 'access_secret_token')

PAIRLIST = config.get('TraderBotFuturesConfig', 'pairList').split(',')
PRICE_INTERVAL = config.get('TraderBotFuturesConfig', 'interval')

SENDER_EMAIL = config.get('Gmail', 'sender_email')
EMAIL_PASSWORD = config.get('Gmail', 'emailpassword')
RECEIVER_EMAIL = config.get('Gmail', 'receiver_email')

EMAIL_FORMAT = 'Subject: {}\n\n{}'
EMAIL_SUBJECT = "TraderBot Futures - An Exception Occurred!"

TEST_MODE = config.getboolean("TraderBotFuturesConfig", "TEST_MODE")
