import os
import sqlite3

path = os.path.dirname(__file__)
database = path + "/data/TraderBot.db"

SQL_CREATE_ORDER_LOG_TABLE = """ CREATE TABLE IF NOT EXISTS ORDER_LOG (
                                    ORDER_ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                                    INSTANCE_ID TEXT,
                                    PAIR TEXT,
                                    ORDER_SIDE TEXT,
                                    QUANTITY REAL,
                                    PRICE REAL); """

SQL_CREATE_PRM_ORDER_TABLE = """ CREATE TABLE IF NOT EXISTS PRM_ORDER (
                                    PAIR TEXT UNIQUE,
                                    PRICE_DECIMAL INTEGER,
                                    QUANTITY_DECIMAL INTEGER,
                                    MINIMUM_QUANTITY REAL,
                                    LONG INTEGER,
                                    SHORT INTEGER,
                                    QUANTITY REAL,
                                    LONG_HOLD INTEGER,
                                    SHORT_HOLD INTEGER,
                                    TRAILING_STOP_LONG_ORDER_ID INTEGER,
                                    TRAILING_STOP_SHORT_ORDER_ID INTEGER); """

SQL_INSERT_INTO_ORDER_LOG = ''' INSERT INTO ORDER_LOG(ORDER_ID,INSTANCE_ID,PAIR,ORDER_SIDE,QUANTITY,PRICE) 
VALUES(?,?,?,?,?,?); '''

SQL_INSERT_INTO_PRM_ORDER = ''' INSERT INTO PRM_ORDER(PAIR,PRICE_DECIMAL,QUANTITY_DECIMAL,MINIMUM_QUANTITY,LONG,SHORT,QUANTITY,LONG_HOLD,SHORT_HOLD,TRAILING_STOP_LONG_ORDER_ID,TRAILING_STOP_SHORT_ORDER_ID) 
VALUES(?,?,?,?,?,?,?,?,?,?,?); '''

SQL_SELECT_FROM_PRM_ORDER = ''' SELECT * FROM PRM_ORDER WHERE PAIR=? '''

SQL_SELECT_ALL_FROM_ORDER_LOG = ''' SELECT * FROM ORDER_LOG WHERE PAIR=?'''

SQL_UPDATE_PRM_ORDER = ''' UPDATE PRM_ORDER SET {} WHERE PAIR=?'''

SQL_DELETE_FROM_ORDER_LOG = ''' DELETE FROM ORDER_LOG WHERE PAIR=? AND ORDER_ID = ?'''

UPDATE_COLUMNS = ['LONG', 'SHORT', 'TRAILING_STOP_LONG_ORDER_ID', 'TRAILING_STOP_SHORT_ORDER_ID']


def connection():
    try:
        conn = sqlite3.connect(database)
        return conn
    except Exception as ex:
        print(ex)


def create_order_log():
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_ORDER_LOG_TABLE)
    except Exception as e:
        print(e)


def create_prm_order():
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_PRM_ORDER_TABLE)
    except Exception as e:
        print(e)


# This function returns all values of parameters.
def select_prm_order(pair):
    conn = connection()
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


def insert_prm_order(parameters):
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_INSERT_INTO_PRM_ORDER, parameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def select_order_log(pair):
    conn = connection()
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


def insert_order_log(orderLogParameters):
    # ORDER_ID
    # INSTANCE_ID
    # PAIR
    # ORDER_SIDE
    # QUANTITY
    # PRICE
    # STOP_PRICE
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_INSERT_INTO_ORDER_LOG, orderLogParameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()


def prm_order_bulk_update(pair, columns, values):
    query = ""
    for column in columns:
        query = query + column + ' = ?,'
    conn = connection()
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


def update_prm_order(pair, column, value):
    conn = connection()
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


def get_latest_order_from_order_log(pair):
    rows = select_order_log(pair=pair)
    # Get orderID of the latest row of order_log table.
    orderId = rows[-1][0]
    return orderId


def remove_from_order_log(pair, orderId):
    conn = connection()
    cursor = conn.cursor()
    try:
        parameters = (pair, orderId)
        cursor.execute(SQL_DELETE_FROM_ORDER_LOG, parameters)
        conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
        conn.close()
