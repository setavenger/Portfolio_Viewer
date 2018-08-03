
import sys

import PortfolioApplication.DatabaseManagement as Dbm
import PortfolioApplication.Computations as Cmp
import PortfolioApplication.Portfolio as Pf
import PortfolioApplication.Speedup as Speed

import PortfolioApplication.DailyUpdate_rmake as DaU

import pandas as pd

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.ticker import PercentFormatter
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

from PortfolioApplication.UserInterface.ShowTransactions import CustomSqlModel as SqlM
import PortfolioApplication.UserInterface.TransactionForms as TransForms

from PyQt5.QtWidgets import QWidget, QMainWindow, QDialog

from datetime import datetime as dt
from datetime import timedelta
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets


class PerformanceWidget(QWidget):
    def __init__(self, parent=None):
        super(PerformanceWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)
        self.axis.set_xlabel('time')
        self.axis.set_ylabel('Performance')

        self.layoutVertical = QtWidgets.QVBoxLayout(self)  # QVBoxLayout
        self.layoutVertical.addWidget(self.canvas)


class AssetDistribution(QWidget):
    def __init__(self, parent=None):
        super(AssetDistribution, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)

        self.layoutVertical = QtWidgets.QVBoxLayout(self)  # QVBoxLayout
        self.layoutVertical.addWidget(self.canvas)


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        # initialize Portfolio
        self.portfolio = Speed.Portfolio()
        DaU.update_all()

        loadUi('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/UserInterface/'
               'UI Templates/Main_main.ui', self)

        '''set the "tables" '''
        self.setWindowTitle("SB Portfolio Manager")

        '''Initiate all relevant selfs'''
        self.sec_dialog = QDialog()
        self.cash_dialog = QDialog()

        '''MenuBar Setup and actions'''
        self.actionShow_Transactions.triggered.connect(self.display_transactions)
        self.actionSecurity.triggered.connect(self.display_securitytransaction)
        self.actionShow_Performance.triggered.connect(self.display_showperformance)
        self.actionCash.triggered.connect(self.display_cashtransaction)
        self.actionShow_Asset_Distribution.triggered.connect(self.display_asset_distribution)

        # make labels clickable
        # self.label.mousePressEvent = self.doSomething

        '''Setup the Performance Widget'''
        self.matplotlibWidget = PerformanceWidget(self)
        self.PlotBackGround.addWidget(self.matplotlibWidget)

        '''Setup Asset Distribution Widget'''
        self.matplotlibWidget2 = AssetDistribution(self)
        self.DistributionBackGround.addWidget(self.matplotlibWidget2)

        self.dateEdit_3.setDate(dt.today())

        # start date
        self.dateEdit.setDate(dt.now() - timedelta(days=365))
        # end date
        self.dateEdit_2.setDate(dt.today())

        # update plots
        self.pushButton.clicked.connect(self.create_performance_plot)
        self.pushButton_2.clicked.connect(self.create_asset_distribution_plot)

        # comboBox Stock
        self.cbox_options()
        # comboBox Benchmark
        self.cbox2_options()

        self.create_performance_plot()
        self.create_asset_distribution_plot()

        '''Setup the Show Transactions Widget'''
        data = SqlM()

        self.tableView.setModel(data)
        self.tableView.setWindowTitle("All Transactions")

    def create_performance_plot(self):  # creates initial plot and updates it
        self.matplotlibWidget.axis.clear()

        stock = self.comboBox.currentText()
        bmark = self.comboBox_2.currentText()

        startdate = self.dateEdit.date().toPyDate()
        enddate = self.dateEdit_2.date().toPyDate()

        # a empty dataframe needs to be created so no errors evolve
        data = pd.DataFrame()
        if stock == "" or bmark == "":
            data = self.get_dataframe(["Dax", "Drone Delivery Canada"], startdate=startdate, enddate=enddate)
        else:
            data = self.get_dataframe([bmark, stock], startdate=startdate, enddate=enddate)
            pass

        self.matplotlibWidget.axis.plot(data)
        self.matplotlibWidget.axis.legend(data.columns)

        self.matplotlibWidget.axis.yaxis.tick_right()

        # removes the frame of the plot
        self.matplotlibWidget.axis.spines['top'].set_visible(False)
        self.matplotlibWidget.axis.spines['right'].set_visible(False)
        self.matplotlibWidget.axis.spines['bottom'].set_visible(False)
        self.matplotlibWidget.axis.spines['left'].set_visible(False)

        self.matplotlibWidget.axis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.3)
        self.matplotlibWidget.axis.yaxis.set_major_formatter(PercentFormatter())
        self.matplotlibWidget.canvas.draw()

    def create_asset_distribution_plot(self):
        self.matplotlibWidget2.axis.clear()

        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return '{v:d} €'.format(v=val)

            return my_autopct

        date = self.dateEdit_3.date().toPyDate()
        date = pd.to_datetime(date)
        df = Dbm.get_spot_portfolio_valuation(pd.to_datetime(date))

        df = df.drop(labels=['Date', 'Total Value'], axis=1)
        df = df.loc[:, (df != 0).any(axis=0)]
        for i in df.columns:
            df.loc[:, i] = round(df.loc[:, i], 3)

        labels = list(df.columns)
        data = list(df.values[0, :])

        self.matplotlibWidget2.axis.pie(data, wedgeprops=dict(width=0.3, linewidth=7, edgecolor='white'), startangle=90,
                                        shadow=False, labels=labels, autopct=make_autopct(data))

        self.matplotlibWidget2.canvas.draw()

    def cbox_options(self):
        # use get stock names function from DatabaseManagement
        self.comboBox.addItems(Dbm.get_stock_names())

    def cbox2_options(self):
        # use get stock names function from DatabaseManagement
        self.comboBox_2.addItems(Dbm.get_index_names())

    '''Functions that open the MenuBarWindows'''
    def display_transactions(self):
        self.stackedWidget.setCurrentIndex(1)

    def display_cashtransaction(self):
        self.cash_dialog.ui = TransForms.CashTransactionForm()
        self.cash_dialog.ui.show()

    def display_securitytransaction(self):
        self.sec_dialog.ui = TransForms.SecurityTransactionForm()
        self.sec_dialog.ui.show()

    def display_showperformance(self):
        self.stackedWidget.setCurrentIndex(0)

    def display_asset_distribution(self):
        self.stackedWidget.setCurrentIndex(2)

    # this function is for label click events
    # def doSomething(self, event):
        # print('Hey')

    def get_dataframe(self, names, startdate, enddate):
        basic = pd.DataFrame()

        # create a DataFrame with columns being the different names
        for name in names:
            df = Dbm.get_prices(name, startdate=startdate, enddate=enddate)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            basic = pd.concat([basic, df], ignore_index=True, axis=1)

        basic.columns = names
        normalized = Cmp.normalize_prices(basic)
        dates = list(normalized.index)

        portfolio = self.portfolio.connector_performance_viewer(dates=dates)
        portfolio.columns = ['Porfolio']
        combined = pd.concat([normalized, portfolio], axis=1)
        combined = combined.fillna(method='ffill')

        return combined


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('MyWindow')

    main = MyWindow()
    main.show()

    sys.exit(app.exec_())
