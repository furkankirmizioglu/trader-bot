import configparser
import os


START_LOG = "{0} - TraderBot Futures has started. Running for {1}"
LONG_POSITION_LOG = "You already carrying long position on these assets: {0}"
SHORT_POSITION_LOG = "You already carrying short position on these assets: {0}"
CANCEL_ORDER_LOG = "{0} - Latest futures {2} order of {1} has cancelled."
PROCESS_TIME_LOG = "This order has processed in {} seconds."

LEVERAGE = 5
USDT = 'USDT'

SUBMIT_ORDER_LOG = "{0} - Futures {2} order for {1} has been submitted at {3} price."
FUTURE_LIMIT_ORDER_TWEET = "{0} - Futures {1} order for {2} has been submitted.\nTake-Profit : {4}\nStop-Limit : {3}"
FUTURE_MARKET_ORDER_TWEET = "{0} - Futures {1} order for {2} has been submitted at market price.\nMarket : {3}"

config = configparser.ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBotFutures.ini"
config.read(dirName)

BINANCE_FUTURES_API_KEY = config.get('BinanceFutures', 'apikey')
BINANCE_FUTURES_API_SECRET_KEY = config.get('BinanceFutures', 'secretkey')
TWITTER_API_KEY = config.get('TwitterAPI', 'consumer_key')
TWITTER_API_SECRET_KEY = config.get('TwitterAPI', 'consumer_secret_key')
TWITTER_ACCESS_TOKEN = config.get('TwitterAPI', 'access_token')
TWITTER_ACCESS_SECRET_TOKEN = config.get('TwitterAPI', 'access_secret_token')
