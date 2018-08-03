
import sqlite3

import pandas as pd
import numpy as np

import PortfolioApplication.Computations as Cmp

tickers = ['^GDAXI', "ETR:SHL", "ETR:IFX", 'PHH2.F', 'ABB.F']
name_list = ['Dax', 'Siemens Healthineers', 'Infineon', 'Paul Hartmann', 'Drone Delivery Canada']
category = ['Index', 'Stock', 'Stock', 'Stock', 'Stock']

db = '/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Portfolio Data'


def new_stocklist():
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS stocklist
                     (name text, symbol text, category text)''')

    conn.commit()
    conn.close()


def read_an_exc(name: str):
    df = pd.read_excel(name)
    data = df.values
    print(df)


def add_stock_excel(name: str):
    df = pd.read_excel(name)
    data = df.values

    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.executemany('''insert into main.stocklist values (?, ?, ?)''', data)

    conn.commit()
    conn.close()


def check_stocklist():
    conn = sqlite3.connect(db)
    sql = "SELECT * FROM stocklist"

    c = conn.cursor()
    c.execute(sql)

    data = c.fetchall()

    names = []
    symbols = []
    c.close()
    conn.close()

    for row in data:
        names.append(row[0])
        symbols.append(row[1])

    return names, symbols


def add_stock(names, symbols, categories):

    namez, symbolz = check_stocklist()

    conn = sqlite3.connect(db)
    c = conn.cursor()

    for i in range(len(symbols)):  # if number of symbols get large change code to executemany statement
        if names[i] not in namez and symbols[i] not in symbolz:
            c.execute("""insert into main.stocklist values (?, ?, ?)""", (names[i], symbols[i], categories[i]))
            print('We just added', names[i], 'to your local Database')
        else:
            print(names[i], 'already listed')
    conn.commit()
    c.close()


# returns numpy array of all names
def get_all_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from stocklist", conn)

    conn.commit()
    conn.close()

    return df['name'].values


def name_to_sym(name):
    conn = sqlite3.connect(db)

    sql = "SELECT * FROM stocklist WHERE name='{}'".format(name)

    c = conn.cursor()
    c.execute(sql)

    row = c.fetchone()

    conn.close()

    return row[1]


def check_if_table_exists(name):
    '''
    insert name of the table you want to check (not the symbol)
    if the table already exists the function will return True
    if the table does not exist function returns False
    '''
    conn = sqlite3.connect(db)

    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(name)

    table = pd.read_sql_query(sql=sql, con=conn)

    conn.close()

    if table.empty is True:
        return False
    elif table.empty is False:
        return True


# returns a numpy array of all the names of the stocks stored in stocklist there are indexes in there to
def get_stock_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from 'stocklist' WHERE category != 'Index'", conn)

    conn.commit()
    conn.close()

    return list(df['name'].values)


# returns a numpy array consisting of the the securities categorised as Index
def get_index_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from 'stocklist' WHERE category = 'Index'", conn)

    conn.commit()
    conn.close()

    return df['name'].values


def upload_security_transaction(date, name, typ, amount, price, fees, tax, notes):
    # typ = buy or sell value buy or sell is passed as string

    amount = Cmp.emptycheck(amount)
    price = Cmp.emptycheck(price)
    fees = Cmp.emptycheck(fees)
    tax = Cmp.emptycheck(tax)

    position = amount * price

    symbol = name_to_sym(name)
# TODO change calculations for buy/sell because fees have to be added to expense but subtracted from cash gain in sales
    total_expense = amount * price + fees + tax

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO main.Transactions values (?,?,?,?,?,?,?,?,?,?,?)",
              (date, name, typ, symbol, amount, price, position, fees, tax, total_expense, notes))
    conn.commit()
    conn.close()


def upload_portfolio_valuation(df: pd.DataFrame):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    checker = check_if_table_exists('PortfolioValuation')

    if not checker:
        df.to_sql('PortfolioValuation', conn)
    elif checker:
        c.execute('''drop table main.PortfolioValuation''')
        df.to_sql('PortfolioValuation', conn)

    conn.commit()
    conn.close()


def upload_cash_transaction(date, typ, amount, fees, tax, notes):
    # typ = Debit or Credit as String

    amount = Cmp.emptycheck(amount)
    fees = Cmp.emptycheck(fees)
    tax = Cmp.emptycheck(tax)

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO main.CashActions values (?,?,?,?,?,?)",
              (date, typ, amount, fees, tax, notes))
    conn.commit()
    conn.close()


def read_transactions():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * FROM main.Transactions", conn)
    conn.close()
    return df


def get_prices(name, startdate=None, enddate=None):
    conn = sqlite3.connect(db)
    query = ""
    if startdate is None and enddate is None:
        query = "SELECT * FROM '{}'".format(name)
    elif enddate is None:
        query = "SELECT * FROM '{}' WHERE DATE > DATE('{}')".format(name, startdate)
    elif startdate is None:
        query = "SELECT * FROM '{}' WHERE DATE < DATE('{}')".format(name, enddate)
    else:
        query = "SELECT * FROM '{}' WHERE DATE > DATE('{}') AND DATE < DATE('{}')".format(name, startdate, enddate)
    df = pd.read_sql_query(query, conn)
    df = df.loc[:, ['Date', 'Adj Close']]
    conn.close()
    return df


def get_transactions():
    conn = sqlite3.connect(db)
    query = '''SELECT * FROM main.Transactions'''
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions


def get_cash_transactions():
    conn = sqlite3.connect(db)
    query = '''SELECT * FROM main.CashActions ORDER BY Date'''
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions


def get_alternative_investments():
    conn = sqlite3.connect(db)
    query = '''SELECT * FROM main.AlternativeInvestments ORDER BY Date'''
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions


def get_portfolio_valuation(start, end):
    conn = sqlite3.connect(db)

    query = "SELECT * FROM main.PortfolioValuation WHERE DATE > DATE('{}') AND DATE < DATE('{}')".format(start, end)

    df = pd.read_sql_query(query, conn, index_col='Date')
    df = df.loc[:, 'Total Value']
    conn.close()
    return df


def get_spot_portfolio_valuation(date):
    conn = sqlite3.connect(db)
    # c = conn.cursor()
    query = "SELECT * FROM main.PortfolioValuation WHERE DATE = '{}'".format(date)

    # c.execute(query)
    # row = c.fetchone()
    data = pd.read_sql_query(query, conn)
    conn.close()

    return data


if __name__ == '__main__':
    add_stock(['iShares TecDAX(DE)', 'Twitter', 'Boeing'], ['EXS2.DE', 'TWR.DE', 'BCO.F'], ['ETF', 'Stock', 'Stock'])
    # add_stock_excel('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Extra Data/SymbolList.xlsx')
    # print(get_spot_portfolio_valuation(pd.to_datetime('2018-04-03')))
