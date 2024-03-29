import os
import sqlite3
import common
import constants

path = os.path.dirname(__file__)
database = path + "/data/TraderBot.db"

SQL_CREATE_ORDER_LOG_TABLE = """ CREATE TABLE IF NOT EXISTS ORDER_LOG (
                                    ORDER_ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                                    INSTANCE_ID TEXT,
                                    PAIR TEXT,
                                    ORDER_SIDE TEXT,
                                    QUANTITY REAL,
                                    PRICE REAL,
                                    STOP_PRICE REAL); """

SQL_CREATE_PRM_ORDER_TABLE = """ CREATE TABLE IF NOT EXISTS PRM_ORDER (
                                    PAIR TEXT UNIQUE,
                                    PRICE_DECIMAL INTEGER,
                                    QUANTITY_DECIMAL INTEGER,
                                    MINIMUM_QUANTITY REAL,
                                    IS_LONG INTEGER,
                                    BUY_HOLD INTEGER,
                                    SELL_HOLD INTEGER,
                                    HAS_BUY_ORDER INTEGER,
                                    HAS_SELL_ORDER INTEGER); """

SQL_INSERT_INTO_ORDER_LOG = ''' INSERT INTO ORDER_LOG(ORDER_ID,INSTANCE_ID,PAIR,ORDER_SIDE,QUANTITY,PRICE,STOP_PRICE) 
VALUES(?,?,?,?,?,?,?); '''

SQL_INSERT_INTO_PRM_ORDER = ''' INSERT INTO PRM_ORDER(PAIR,PRICE_DECIMAL,QUANTITY_DECIMAL,MINIMUM_QUANTITY,IS_LONG,BUY_HOLD,SELL_HOLD,HAS_BUY_ORDER,HAS_SELL_ORDER) 
VALUES(?,?,?,?,?,?,?,?,?); '''

SQL_SELECT_FROM_PRM_ORDER = ''' SELECT * FROM PRM_ORDER WHERE PAIR=? '''

SQL_SELECT_ALL_FROM_ORDER_LOG = ''' SELECT * FROM ORDER_LOG WHERE PAIR=?'''

SQL_UPDATE_PRM_ORDER = ''' UPDATE PRM_ORDER SET {} WHERE PAIR=?'''

SQL_DELETE_FROM_ORDER_LOG = ''' DELETE FROM ORDER_LOG WHERE PAIR=? AND ORDER_ID = ?'''

UPDATE_COLUMNS = ['IS_LONG', 'HAS_BUY_ORDER', 'HAS_SELL_ORDER']

PAIRLIST = constants.PAIRLIST


def createConnection():
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Exception as ex:
        print(ex)
    return conn


def createOrderLogTable():
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_ORDER_LOG_TABLE)
    except Exception as e:
        print(e)


def createPrmOrderTable():
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_PRM_ORDER_TABLE)
    except Exception as e:
        print(e)


# This function returns all values of parameters.
def selectAllFromPrmOrder(pair):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        pair = (pair,)
        cursor.execute(SQL_SELECT_FROM_PRM_ORDER, pair)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as ex:
        print(ex)
        conn.close()


def insertIntoPrmOrder(parameters):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_INSERT_INTO_PRM_ORDER, parameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def selectAllFromOrderLog(pair):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        pair = (pair,)
        cursor.execute(SQL_SELECT_ALL_FROM_ORDER_LOG, pair)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as ex:
        print(ex)
        conn.close()


# orderLogParams1 = (1234, '01/10/2022 13:14:14', 'DYDXBUSD', 'BUY', 5.2, 1.27, 1.37)
# insertIntoOrderLog(orderLogParameters=orderLogParams1)
def insertIntoOrderLog(orderLogParameters):
    # ORDER_ID
    # INSTANCE_ID
    # PAIR
    # ORDER_SIDE
    # QUANTITY
    # PRICE
    # STOP_PRICE
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_INSERT_INTO_ORDER_LOG, orderLogParameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def bulkUpdatePrmOrder(pair, columns, values):
    query = ""
    for column in columns:
        query = query + column + ' = ?,'
    conn = createConnection()
    c = conn.cursor()
    query = query[:-1]
    try:
        values += (pair,)
        c.execute(SQL_UPDATE_PRM_ORDER.format(query), values)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def updatePrmOrder(pair, column, value):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        column = column + "=?"
        query = SQL_UPDATE_PRM_ORDER.format(column)
        queryParameters = (value, pair)
        cursor.execute(query, queryParameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def getLatestOrderFromOrderLog(pair):
    rows = selectAllFromOrderLog(pair=pair)
    # Get orderID of the latest row of order_log table.
    orderId = rows[-1][0]
    return orderId


def removeLogFromOrderLog(pair, orderId):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        parameters = (pair, orderId)
        cursor.execute(SQL_DELETE_FROM_ORDER_LOG, parameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def initPrmOrderTable(pair):
    createPrmOrderTable()
    createOrderLogTable()
    rows = selectAllFromPrmOrder(pair=pair)
    if len(rows) == 0:
        priceDec, qtyDec = common.decimal_place(pair=pair)
        minQty = common.getMinimumQuantity(pair=pair)
        isLong = 0          # Default value
        buyHold = 0         # Default value
        sellHold = 0        # Default value
        hasBuyOrder = 0     # Default value
        hasSellOrder = 0    # Default value
        parameters = (pair, priceDec, qtyDec, minQty, isLong, buyHold, sellHold, hasBuyOrder, hasSellOrder)
        insertIntoPrmOrder(parameters=parameters)


def getHasBuyOrder(pair):
    data = selectAllFromPrmOrder(pair=pair)
    return data[-1][7]


def getIsLong(pair):
    data = selectAllFromPrmOrder(pair=pair)
    return data[-1][4]


def getDecimals(pair):
    data = selectAllFromPrmOrder(pair=pair)
    return data[-1][1], data[-1][2]


def getMinimumQuantity(pair):
    data = selectAllFromPrmOrder(pair=pair)
    return data[-1][3]
