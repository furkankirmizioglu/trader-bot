from configparser import ConfigParser
import os

config = ConfigParser()
dirName = os.path.dirname(__file__) + "/BinanceBot.ini"
config.read(dirName)

API_KEY = config.get("BinanceSignIn", "apikey")
API_SECRET_KEY = config.get("BinanceSignIn", "secretkey")

TWITTER_API_KEY = config.get('TwitterAPI', 'consumer_key')
TWITTER_API_SECRET_KEY = config.get('TwitterAPI', 'consumer_secret_key')
TWITTER_ACCESS_TOKEN = config.get('TwitterAPI', 'access_token')
TWITTER_ACCESS_SECRET_TOKEN = config.get('TwitterAPI', 'access_secret_token')

FIREBASE_DEVICE_KEY = config.get('FirebaseAPI', 'device_key')

SENDER_EMAIL = config.get('Gmail', 'sender_email')
EMAIL_PASSWORD = config.get('Gmail', 'emailpassword')
RECEIVER_EMAIL = config.get('Gmail', 'receiver_email')

PRICE_INTERVAL = config.get("TraderBotConfig", "interval")
PAIRLIST = config.get("TraderBotConfig", "pairlist").split(',')
TEST_MODE = config.getboolean("TraderBotConfig", "TEST_MODE")

MIN_AMOUNT_EXCEPTION_LOG = "{0} - Buy amount cannot be less than {2} USDT! {1} buy order is invalid and won't submit."
START_LOG = "{0} - TraderBot has started. Running for {1}"
CANCEL_ORDER_LOG = "{0} - Latest {2} order of {1} has canceled."
PROCESS_TIME_LOG = "This cycle has finished in {} seconds."
INITIAL_LOG = "{0} - {1} | Price: {2} | Z-Score: {3} | Top: {4} | Bottom: {5}"
HAVE_ASSET_LOG = "You already purchased these assets: {0}"
STOP_LIMIT_ORDER_LOG = "{0} - {2} order for {1} has submitted.\nLimit : {3}"
OCO_ORDER_LOG = "{0} - {1} order for {2} has submitted.\nLimit : {3} | Stop-Limit: {4}"

NOTIFIER_TITLE = "You have a new trade activity !"
NOTIFIER_CANCEL_ORDER_LOG = "Latest {0} order for {1} has canceled."
NOTIFIER_STOP_LIMIT_ORDER_LOG = "{0} order for {1} has submitted.\nLimit: {2}"
NOTIFIER_OCO_ORDER_LOG = "{0} order for {1} has submitted.\nLimit: {2} | Stop-Limit: {3}"

EMAIL_FORMAT = 'Subject: {}\n\n{}'
EMAIL_SUBJECT = "An Exception Occurred!"

BUSD = 'BUSD'
USDT = 'USDT'
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
MIN_USD = 12
RSI_PERIOD = 14
ATR_PERIOD = 14
