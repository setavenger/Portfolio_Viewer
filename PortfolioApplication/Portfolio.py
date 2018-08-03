
import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


import PortfolioApplication.DatabaseManagement as Dbm
import PortfolioApplication.Computations as Cmp

'''
The portfolio returns are calculated Time-Weighted Rate of Return (TWRoR)
Therefore therefore the breakpoints of Cash flows need to be determined see self.fund_states

These rows are linked to their contents (assets and cash) which will then generate a return
Then the TWRoR will be calculated and will the return in this point in time
'''


class Portfolio:
    '''The Basic Structure while operating on Transactions made and any portfolio related calculations'''
    # initialize with transactions data so you have the data immediately and can start transforming it
    def __init__(self):
        # create basic properties of the class
        self.assets = []
        self.cash_actions = Dbm.get_cash_transactions()
        self.stats = pd.DataFrame(columns=['Asset', 'Amount', 'Position'])
        self.fund_states = pd.DataFrame(columns=['Date', 'ID'])
        self.transactions_list = Dbm.read_transactions()
        self.transactions_list['Transaction_ID'] = np.array(range(0, len(self.transactions_list['Date'])))
        self.cash_actions['Transaction_ID'] = np.array(range(1000, len(self.cash_actions['Date'])+1000))
        self.contents = pd.DataFrame(columns=['Date', 'Buy/Sell', 'Asset', 'Amount', 'Price', 'Fees', 'ID'])
        self.spot_amounts = pd.DataFrame(columns=['Asset', 'Amount', 'Position'])

        # start doing calculations and create basic structure of the portfolio data
        self.create_fund_states()
        self.map_transactions()
        self.map_start_cash()

        self.initialize_stats()
        self.fill_stats()

        # master most recent all star inclusions all most all relevant information included
        self.combined_transactions = self.merge_transactions()
        self.portfolio = self.form_portfolio()
        # self.amount_schedule = self.create_amount_schedule(list(self.fund_states['Date']))

        # characteristics
        self.portfolio_opening = self.portfolio_start().values[0]

        # valuation of all positions
        # TODO Valuation of Alternatives is still to high because losses ar not properly integrated
        self.portfolio_valuation = self.create_portfolio_value()

    def initialize_stats(self):
        df = self.transactions_list
        for name in df['Security']:
            if name not in self.assets:
                self.assets.append(name)
                inputs = [[name, 0, 0]]
                stat_data = self.stats.values
                new_data = np.append(stat_data, inputs, axis=0)
                self.stats = pd.DataFrame(data=new_data, columns=['Asset', 'Amount', 'Position'])

    def create_fund_states(self):

        self.fund_states['Date'] = self.cash_actions['Date']
        self.fund_states.loc[0, ['ID']] = 0
        # remove duplicates and reinstate indexes
        self.fund_states = self.fund_states.drop_duplicates(subset='Date')
        self.fund_states = self.fund_states.reset_index(drop=True)

        # set date and ID
        for i in range(1, len(self.fund_states)):
            self.fund_states.loc[i, ['ID']] = self.fund_states.loc[i-1, ['ID']] + 1
        # self.fund_states = self.fund_states.drop_duplicates(subset='Date')

        # create the content frame
        '''
        the structure for funds is the self.fund_states where all breakpoints are included 
        (where Cash In- or Outflows appeared)
        
        followed by the sub table with each transaction having its identifier linking it to the 
        fund_state it appeared in
        '''

    def map_transactions(self):
        reverse = self.fund_states[::-1]
        checked = []
        data = np.empty((1, 7))
        # maps each transaction to each state/phase
        for i in range(0, len(reverse['Date'])):
            ident = self.fund_states.loc[len(reverse['Date']) - i - 1, ['ID']]
            # the bigger value is the later value
            for index in range(0, len(self.transactions_list['Date'])):

                border = pd.to_datetime(reverse.loc[len(reverse['Date']) - i - 1, ['Date']])
                checker = pd.to_datetime(self.transactions_list.loc[index, ['Date']])
                trans_id = list(self.transactions_list.loc[index, ['Transaction_ID']])

                if border[0] <= checker[0] and trans_id[0] not in checked:
                    transaction = self.transactions_list.loc[index, ['Date', 'Buy/Sell', 'Security',
                                                                     'Amount', 'Price', 'Fees']]
                    transaction = transaction.values

                    appendix = ident.values
                    transaction = np.append(transaction, appendix, axis=0)
                    data = np.append(data, [transaction], axis=0)

                    checked.append(trans_id)

        self.contents = pd.DataFrame(data=data[1:, :], columns=['Date', 'Buy/Sell', 'Asset',
                                                                'Amount', 'Price', 'Fees', 'ID'])

        '''creates a pandas DataFrame where all made Transactions are mapped to the state/ phase they occured in'''

    def map_start_cash(self):
        reverse = self.fund_states[::-1]
        checked = []
        data = self.contents.values

        for i in range(0, len(reverse['Date'])):
            ident = self.fund_states.loc[len(reverse['Date']) - i-1, ['ID']]
            # the bigger value is the later value
            for index in range(0, len(self.cash_actions['Date'])):
                border = pd.to_datetime(reverse.loc[len(reverse['Date']) - i - 1, ['Date']])
                checker = pd.to_datetime(self.cash_actions.loc[index, ['Date']])
                trans_id = list(self.cash_actions.loc[index, ['Transaction_ID']])

                if border[0] <= checker[0] and trans_id[0] not in checked:
                    transaction = self.cash_actions.loc[index, ['Date', 'Debit/Credit', 'Amount', 'Fees']]
                    transaction = transaction.values
                    transaction = np.insert(transaction, 2, 'Cash')
                    transaction = np.insert(transaction, 4, 1)
                    if transaction[1] == 'Credit':
                        val = transaction[3]
                        transaction[3] = val * -1

                    appendix = ident.values

                    transaction = np.append(transaction, appendix, axis=0)
                    data = np.append(data, [transaction], axis=0)

                    checked.append(trans_id)

        self.contents = pd.DataFrame(data=data[1:, :], columns=['Date', 'Buy/Sell', 'Asset', 'Amount', 'Price',
                                                                'Fees', 'ID'])

    def fill_stats(self):
        df = self.transactions_list
        data = self.stats.values
        for i in range(df.shape[0]):
            # row = transaction
            row = df.loc[i, ['Security', 'Buy/Sell', 'Amount', 'Position']].values
            name = row[0]

            stats_row_index = self.assets.index(name)

            if row[1] == 'Buy':
                position = float(data[stats_row_index, 2])
                position += row[3]
                data[stats_row_index, 2] = position

                amount = float(data[stats_row_index, 1])
                amount += row[2]
                data[stats_row_index, 1] = amount

            elif row[1] == 'Sell':
                position = float(data[stats_row_index, 2])
                position -= row[3]
                data[stats_row_index, 2] = float(position)

                amount = float(data[stats_row_index, 1])
                amount -= row[2]
                data[stats_row_index, 1] = amount

        self.stats = pd.DataFrame(data=data, columns=['Asset', 'Amount', 'Position'])

    def visualize(self):
        data = self.stats.loc[:, 'Position']
        labels = self.stats.loc[:, 'Asset']
        plt.pie(data, labels=labels)
        plt.show()

    def get_period_expenses(self, ident):
        cash_out = pd.DataFrame(columns=['Outs'])
        cash_in = pd.DataFrame(columns=['Ins'])
        buy = self.contents.loc[(self.contents['ID'] == ident) &  # (self.contents['Asset'] != 'Cash') &
                                (self.contents['Buy/Sell'] == 'Buy')]
        sell = self.contents.loc[(self.contents['ID'] == ident) &  # (self.contents['Asset'] != 'Cash') &
                                 (self.contents['Buy/Sell'] == 'Sell')]

        cash_out['Outs'] = buy['Amount'] * buy['Price'] + buy['Fees']
        cash_in['Ins'] = sell['Amount'] * sell['Price'] - sell['Fees']

        net = cash_out['Outs'].sum()*-1 + cash_in['Ins'].sum()
        return net

    def create_spot_component(self, date):
        transactions = self.transactions_list
        cash_move = self.cash_actions

        transactions['Date'] = pd.to_datetime(transactions['Date'])
        mask = (transactions['Date'] < date)
        transactions = transactions.loc[mask]

        cash_move['Date'] = pd.to_datetime(cash_move['Date'])
        mask = (cash_move['Date'] < date)
        cash_move = cash_move.loc[mask]

        data = self.stats.values

        data[:, 1:] = 0
        data = np.append(data, [['Cash', 0, 0]], axis=0)

        for i in transactions.index:
            # row = transaction

            row = transactions.loc[i, ['Security', 'Buy/Sell', 'Amount', 'Position', 'Date', 'Fees']].values

            name = row[0]

            stats_row_index = self.assets.index(name)

            if row[1] == 'Buy':
                position = float(data[stats_row_index, 2])
                position -= row[3]
                position -= row[5]

                cash = float(data[-1, 1])
                cash -= row[3]
                cash -= row[5]
                data[stats_row_index, 2] = position
                data[-1, 1] = cash

                amount = float(data[stats_row_index, 1])
                amount += row[2]
                data[stats_row_index, 1] = amount

            elif row[1] == 'Sell':
                position = float(data[stats_row_index, 2])
                position += row[3]
                position -= row[5]

                cash = float(data[-1, 1])
                cash += row[3]
                cash -= row[5]

                data[stats_row_index, 2] = position
                data[-1, 1] = cash

                amount = float(data[stats_row_index, 1])
                amount -= row[2]
                data[stats_row_index, 1] = amount

        for i in cash_move.index:
            row = cash_move.loc[i, ['Debit/Credit', 'Amount', 'Date', 'Fees']].values

            if row[0] == 'Debit':
                cash = float(data[-1, 1])
                cash += row[1]
                cash -= row[3]

                data[-1, 1] = cash

            elif row[1] == 'Credit':

                cash = float(data[-1, 1])
                cash += row[1]
                cash -= row[3]

                data[-1, 1] = cash

        self.spot_amounts = pd.DataFrame(data=data, columns=['Asset', 'Amount', 'Position'])

    def get_net_cash(self, date=dt.datetime.today()):
        transactions = self.cash_actions
        transactions.loc[:, ['Date']] = pd.to_datetime(transactions['Date'])
        mask_date = (transactions['Date'] <= date)
        transactions = self.cash_actions.loc[mask_date]
        mask = (transactions['Debit/Credit'] == 'Debit')
        debit = transactions.loc[mask]
        debit = debit.loc[:, ['Amount']].sum()

        mask = (transactions['Debit/Credit'] == 'Credit')
        credit = transactions.loc[mask]
        credit = credit.loc[:, ['Amount']].sum()

        net_cash = debit - credit
        # Fix cash output
        return float(net_cash)

    def get_fees(self, date=dt.datetime.today()):
        transactions = self.combined_transactions
        transactions.loc[:, ['Date']] = pd.to_datetime(transactions['Date'])
        mask_date = (transactions['Date'] <= pd.to_datetime(date))
        transactions = transactions.loc[mask_date]

        fees = transactions['Fees'].sum()

        return float(fees)

    def get_amount(self, name, date=dt.datetime.today()):
        transactions = self.transactions_list
        transactions.loc[:, ['Date']] = pd.to_datetime(transactions['Date'])
        mask = ((transactions['Date'] <= pd.to_datetime(date)) & (transactions['Security'] == name))

        transactions = transactions.loc[mask]
        buy_mask = (transactions['Buy/Sell'] == 'Buy')
        sell_mask = (transactions['Buy/Sell'] == 'Sell')

        buys = transactions.loc[buy_mask]
        sells = transactions.loc[sell_mask]
        increase = buys['Amount'].sum()
        decrease = sells['Amount'].sum()

        return float(increase - decrease)

    # gets the amount of Alternate considering that alternate only has a value and no amounts those will be set the same
    def alternate_amount(self, date):
        mask = (self.combined_transactions['Date'] <= pd.to_datetime(date))
        transactions = self.combined_transactions.loc[mask]

        mask = (transactions['Security'] == 'Alternate')
        interim = transactions.loc[mask]

        # adjust bookings
        interim = interim.set_index('Date')
        change = interim.loc[:, ['Change']].sum()

        # adjust bookings
        extras = Dbm.get_alternative_investments()
        extras = extras.loc[:, ['Date', 'NetChange']]
        extras.loc[:, ['Date']] = extras.loc[:, ['Date']].apply(pd.to_datetime)

        mask2 = (extras['Date'] <= pd.to_datetime(date))

        extras = extras.loc[mask2]
        adjustment = extras.loc[:, ['NetChange']].sum()

        adj_change = float(change) - float(adjustment)
        return adj_change

    def create_amount_schedule(self, dates=None, date_is_index=False):
        if dates is None:
            return

        securities = self.portfolio.columns
        amounts = np.empty((1, len(securities)))
        if dates is not None:
            dates.append(pd.datetime.now().date())
            for i in range(0, len(dates)):
                date = dates[len(dates)-i-1]
                interim = []
                for asset in securities:
                    if asset != 'Cash' and asset != 'Alternate':
                        amount = self.get_amount(name=asset, date=date)
                        interim.append(amount)
                    elif asset == 'Alternate':
                        interim.append(self.alternate_amount(date=date))
                    else:
                        mask = (self.combined_transactions['Date'] <= pd.to_datetime(date))
                        transactions = self.combined_transactions.loc[mask]

                        # compute the cash position left after all transactions fees
                        cash = transactions['Change'].sum()
                        # the sum of all fees that happend in that TimeFrame are computed
                        cash -= self.get_fees(date=date)
                        interim.append(cash)
                amounts = np.append(amounts, [interim], axis=0)

        amounts = np.flip(amounts[1:, :], axis=0)
        if not date_is_index:
            '''if dateindex is False the Dates will be in a column names Date if set to True see below'''
            columns = list(securities) + ['Date']
            new_dates = np.empty((1, 1))
            for i in dates:
                new_dates = np.append(new_dates, [[i]], axis=0)
            amounts = np.append(amounts, new_dates[1:], axis=1)
            schedule = pd.DataFrame(data=amounts[:-1], columns=columns)

            schedule.loc[:, ['Alternate']] = schedule.loc[:, ['Alternate']].round(3)
            schedule.loc[:, ['Cash']] = schedule.loc[:, ['Cash']].round(3)

            return schedule
        elif date_is_index:
            '''if date index is True the date will be an Index an not a column as in standard setting'''
            columns = list(securities) + ['Date']
            new_dates = np.empty((1, 1))
            for i in dates:
                new_dates = np.append(new_dates, [[i]], axis=0)
            amounts = np.append(amounts, new_dates[1:], axis=1)
            schedule = pd.DataFrame(data=amounts[:-1], columns=columns)

            schedule.loc[:, ['Alternate']] = schedule.loc[:, ['Alternate']].round(3)
            schedule.loc[:, ['Cash']] = schedule.loc[:, ['Cash']].round(3)

            schedule = schedule.set_index('Date')

            return schedule

    def merge_transactions(self):
        frame = pd.DataFrame(columns=['Date', 'Security', 'In/Out', 'Change', 'Fees', 'Tax'])

        cash = Dbm.get_cash_transactions()
        stocks = Dbm.get_transactions()
        alter = Dbm.get_alternative_investments()

        # get the essentials
        cash = cash.loc[:, ['Date', 'Debit/Credit', 'Amount', 'Fees', 'Tax']]
        stocks = stocks.loc[:, ['Date', 'Security', 'Buy/Sell', 'Amount', 'Price', 'Fees', 'Tax']]

        # same width

        stocks.loc[:, 'Change'] = stocks['Amount'] * stocks['Price']
        stocks = stocks.drop(['Amount', 'Price'], axis=1)

        # uniform increase decrease
        stocks.loc[:, 'In/Out'] = stocks['Buy/Sell'].apply(self.true_false)
        cash.loc[:, 'In/Out'] = cash['Debit/Credit'].apply(self.true_false)
        alter.loc[:, 'In/Out'] = alter['Buy/Sell'].apply(self.true_false)

        cash.loc[:, 'Change'] = cash['Amount']
        alter.loc[:, 'Change'] = alter['Amount']

        cash.loc[:, 'Security'] = 'Cash'
        alter.loc[:, 'Security'] = 'Alternate'

        # order the columns [Date, Buy/Sell, Change, Fees, tax]
        stocks = stocks.loc[:, ['Date', 'Security', 'In/Out', 'Change', 'Fees', 'Tax']]
        cash = cash.loc[:, ['Date', 'Security', 'In/Out', 'Change', 'Fees', 'Tax']]
        alter = alter.loc[:, ['Date', 'Security', 'In/Out', 'Change', 'Fees', 'Tax']]

        frame = frame.append(stocks, ignore_index=True)
        frame = frame.append(cash, ignore_index=True)
        frame = frame.append(alter, ignore_index=True)

        # comparison is used because 'if cond is True' gives ERROR
        buy_mask = (frame['In/Out'] == True)
        buys = frame.loc[buy_mask].copy()
        buys.loc[:, ['Change']] = buys['Change'].apply(self.turn_negative)

        sell_mask = (frame['In/Out'] == False)
        sells = frame.loc[sell_mask]

        frame = pd.DataFrame(columns=['Date', 'Security', 'In/Out', 'Change', 'Fees', 'Tax'])
        frame = frame.append(buys, ignore_index=True)
        frame = frame.append(sells, ignore_index=True)

        frame.loc[:, ['Date']] = pd.to_datetime(frame['Date'])
        frame = frame.sort_values(by='Date')
        frame = frame.reset_index(drop=True)

        return frame

    def form_portfolio(self, date=dt.datetime.today()):
        mask = (self.combined_transactions['Date'] < date)
        transactions = self.combined_transactions.loc[mask]

        assets = []
        positions = []
        amounts = []

        fees = 0
        cash = transactions['Change'].sum()
        for asset in list(transactions['Security']):
            if asset not in assets and asset != 'Cash':
                assets.append(asset)

        for asset in assets:
            if asset != 'Cash':
                mask = (transactions['Security'] == asset)
                interim = transactions.loc[mask]
                change = interim['Change'].sum()
                positions.append(change)
                fees += interim['Fees'].sum()
                amount = self.get_amount(name=asset, date=date)
                amounts.append(amount)

            elif asset == 'Cash':
                mask = (transactions['Security'] == asset)
                interim = transactions.loc[mask]
                fees += interim['Fees'].sum()

        cash -= fees
        positions.append(cash)
        amounts.append(0)
        names = (assets + ['Cash'])
        structure = pd.DataFrame(data=[positions, amounts], columns=names, index=['Position', 'Amount'])
        if 'Alternate' in structure.columns:
            structure.loc['Amount', ['Alternate']] = structure.loc['Position', ['Alternate']]
        return structure

    def create_portfolio_value(self, dates: list=None):
        if dates is None:
            dates = self.daterange_opening()
        portfolio_amounts = self.create_amount_schedule(dates=dates)
        data_request = list(filter(lambda x: x != 'Alternate' and x != 'Cash' and x != 'Date',
                                   portfolio_amounts.columns))
        names = data_request

        basic = pd.DataFrame()

        # create a DataFrame with columns being the different names
        for name in data_request:
            df = Dbm.get_prices(name, startdate=dates[0], enddate=dates[-1])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            basic = pd.concat([basic, df], ignore_index=True, axis=1)

        structure = self.create_amount_schedule(dates=list(basic.index), date_is_index=True)

        # basic = basic.apply(lambda x: int(x))
        basic.columns = names
        basic = Cmp.test_gaps(basic)

        for i in data_request:
            structure.loc[:, i] = structure[i].multiply(basic[i])

        structure.loc[:, ['Alternate']] = structure.loc[:, ['Alternate']].apply(abs)
        # structure = structure.drop('Alternate', axis=1)
        # create sum of value column
        data = structure.values
        sums = np.nansum(data, axis=1)

        with_sums = np.concatenate((data.T, np.array([sums])), axis=0).T

        columns = list(structure.columns) + ['Total Value']
        portfolio_value_dist = pd.DataFrame(data=with_sums, columns=columns, index=structure.index)

        return portfolio_value_dist

    def portfolio_start(self):
        return self.combined_transactions.loc[0, ['Date']]

    def plot_performance(self):
        to_plot = self.normalize()

        fig, ax = plt.subplots()

        ax.set_xlabel('time')
        ax.set_ylabel('Performance')

        ax.yaxis.set_major_formatter(PercentFormatter())

        ax.plot(to_plot)
        # to_plot.plot()
        plt.show()

    @staticmethod
    def true_false(x):
        x = str(x)
        if x == "Credit" or x == 'Buy':
            x = True
        elif x == 'Debit' or x == 'Sell':
            x = False

        return x

    @staticmethod
    def turn_negative(x: float):
        return -x

    def normalize(self, simple: bool=True):
        if simple:
            return self.normalize_prices_simp()
        else:
            return self.normalize_prices_twrr()

    # get simple returns
    def normalize_prices_simp(self, df=None):
        if df is None:
            df = self.portfolio_valuation.loc[:, 'Total Value']
        dates = self.fund_states['Date']
        dates_to_value = np.zeros((1, 2))
        for date in dates:
            index = df.index.get_loc(date)
            dates_to_value = np.append(dates_to_value, [[date, df.iloc[index]]], axis=0)

        tracking = []
        if isinstance(df, pd.Series):
            structure = np.empty((1, 2))
            dates = self.fund_states['Date']
            dates_to_value = np.zeros((1, 2))
            for date in dates:
                index = df.index.get_loc(date)
                dates_to_value = np.append(dates_to_value, [[date, df.iloc[index]]], axis=0)
            date_to_value_series = pd.Series(data=dates_to_value[:, 1], index=dates_to_value[:, 0])

            for date in reversed(dates_to_value[1:, 0]):
                start = float(date_to_value_series.loc[date])

                # mask = (df > pd.to_datetime(date))
                interim_no_ind = df.reset_index()
                interim_no_ind.loc[:, ['Date']] = interim_no_ind.loc[:, ['Date']].apply(pd.to_datetime)
                if len(tracking) == 0:
                    mask = (interim_no_ind['Date'] >= pd.to_datetime(date))
                else:
                    mask = ((interim_no_ind['Date'] >= pd.to_datetime(date)) &
                            (interim_no_ind['Date'] < pd.to_datetime(tracking[-1])))
                interim = interim_no_ind.loc[mask]
                interim = interim.dropna()
                interim = interim.set_index('Date')

                cashbase = self.get_net_cash(date)
                interim = interim.apply(lambda x: (x / cashbase) * 100)
                data = interim.reset_index().values
                structure = np.append(structure, data, axis=0)

                tracking.append(date)

            output = pd.DataFrame(data=structure[1::], columns=['Date', 'Return'])
            # output.loc[:, ['Date']] = output.loc[:, ['Date']].apply(pd.to_datetime)

            output = output.set_index('Date')
            output = output.sort_index(axis=0)

            return output
        else:
            pass

    # normalizes for Time Weighted Rate of Return
    def normalize_prices_twrr(self):
        df = self.portfolio_valuation.loc[:, 'Total Value']
        dates = self.fund_states['Date']
        dates_to_value = np.zeros((1, 2))
        for date in dates:
            index = df.index.get_loc(date)
            dates_to_value = np.append(dates_to_value, [[date, df.iloc[index]]], axis=0)

        tracking = []
        if isinstance(df, pd.Series):
            structure = np.empty((1,2))
            dates = self.fund_states['Date']
            dates_to_value = np.zeros((1, 2))
            for date in dates:
                index = df.index.get_loc(date)
                dates_to_value = np.append(dates_to_value, [[date, df.iloc[index]]], axis=0)
            date_to_value_series = pd.Series(data=dates_to_value[:, 1], index=dates_to_value[:, 0])

            for date in reversed(dates_to_value[1:, 0]):
                start = float(date_to_value_series.loc[date])

                # mask = (df > pd.to_datetime(date))
                interim_no_ind = df.reset_index()
                interim_no_ind.loc[:, ['Date']] = interim_no_ind.loc[:, ['Date']].apply(pd.to_datetime)
                if len(tracking) == 0:
                    mask = (interim_no_ind['Date'] >= pd.to_datetime(date))
                else:
                    mask = ((interim_no_ind['Date'] >= pd.to_datetime(date)) &
                            (interim_no_ind['Date'] < pd.to_datetime(tracking[-1])))
                interim = interim_no_ind.loc[mask]
                interim = interim.dropna()
                interim = interim.set_index('Date')

                interim = interim.apply(lambda x: (x / start) * 100)
                data = interim.reset_index().values
                structure = np.append(structure, data, axis=0)

                tracking.append(date)

            output = pd.DataFrame(data=structure[1::], columns=['Date', 'Return'])
            # output.loc[:, ['Date']] = output.loc[:, ['Date']].apply(pd.to_datetime)

            output = output.set_index('Date')
            output = output.sort_index(axis=0)

            return output
        else:
            pass

    def daterange_opening(self, date1=None, date2=None):
        '''Creates a list of Dates from date1 to date2'''
        if date1 is None:
            date1 = self.portfolio_opening
        if date2 is None:
            date2 = dt.datetime.today()
        dates = []
        for n in range(int((date2 - date1).days) + 1):
            dates.append(date1 + dt.timedelta(n))

        return dates

    @staticmethod
    def daterange(date1, date2):
        dates = []
        for n in range(int((date2 - date1).days) + 1):
            dates.append(date1 + dt.timedelta(n))

        return dates

    # Here come the connectors which link this Class to the other files and operations
    def connector_performance_viewer(self, dates: list):
        '''crates a series which can be appended to the performance_viewer DataFrame'''
        df = self.create_portfolio_value(dates=dates)
        d = df.loc[:, ['Total Value']]
        s = df.loc[:, 'Total Value']
        f = df.index
        series = df.loc[:, 'Total Value']
        normalized = self.normalize_prices_simp(df=series)
        return normalized


# TODO expense already mapped but still need to arrange the code order/structure still error message
# TODO cash after period calculation is based on before mentioned to-do
# TODO there is still need to get the end Cash_balance
if __name__ == '__main__':
    portfolio = Portfolio()

    # def daterange(date1, date2):
    #     dates = []
    #     for n in range(int((date2 - date1).days) + 1):
    #         dates.append(date1 + dt.timedelta(n))
    #
    #     return dates
    #
    # start_dt = portfolio.portfolio_opening
    # end_dt = dt.datetime.today()
    #
    # ddf = daterange(start_dt, end_dt)
    #
    # portfolio.plot_performance()
    # # portfolio.create_amount_schedule(dates=ddf, date_is_index=True).to_excel('AmountSchedule.xlsx')
    # # portfolio.combined_transactions.to_excel('CombinedTransactions.xlsx')
    portfolio.portfolio_valuation.to_excel('PortfolioValuation.xlsx')
