

import PortfolioApplication.DatabaseManagement as Dbm
import PortfolioApplication.Computations as Cmp
import pandas as pd

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.ticker import PercentFormatter
from matplotlib.figure import Figure

from PortfolioApplication.UserInterface.ShowTransactions import CustomSqlModel as SqlM
import PortfolioApplication.UserInterface.TransactionForms as TransForms

from PyQt5.QtWidgets import QWidget, QMainWindow, QDialog

from datetime import datetime as dt
from datetime import timedelta
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)
        self.axis.set_xlabel('time')
        self.axis.set_ylabel('Performance')

        self.layoutVertical = QtWidgets.QVBoxLayout(self)  # QVBoxLayout
        self.layoutVertical.addWidget(self.canvas)


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        loadUi('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/UserInterface/'
               'UI Templates/Main_main.ui', self)

        '''Initiate all relevant selfs'''
        self.sec_dialog = QDialog()
        self.cash_dialog = QDialog()

        '''MenuBar Setup and actions'''
        self.actionShow_Transactions.triggered.connect(self.display_transactions)
        self.actionSecurity.triggered.connect(self.display_securitytransaction)
        self.actionShow_Performance.triggered.connect(self.display_showperformance)
        self.actionCash.triggered.connect(self.display_cashtransaction)

        # make labels clickable
        # self.label.mousePressEvent = self.doSomething

        '''Setup the Performance Widget'''
        self.matplotlibWidget = MatplotlibWidget(self)
        self.PlotBackGround.addWidget(self.matplotlibWidget)

        # start date
        self.dateEdit.setDate(dt.now() - timedelta(days=365))
        # end date
        self.dateEdit_2.setDate(dt.today())

        self.pushButton.clicked.connect(self.get_plot)

        # comboBox Stock
        self.cbox_options()
        # comboBox Benchmark
        self.cbox2_options()

        self.get_plot()

        '''Setup the Show Transactions Widget'''
        data = SqlM()

        self.tableView.setModel(data)
        self.tableView.setWindowTitle("All Transactions")

    def get_plot(self):  # creates initial plot and updates it
        self.matplotlibWidget.axis.clear()

        stock = self.comboBox.currentText()
        bmark = self.comboBox_2.currentText()

        startdate = self.dateEdit.date().toPyDate()
        enddate = self.dateEdit_2.date().toPyDate()
        if stock == "" or bmark == "":
            data = get_dataframe(["Dax", "Drone Delivery Canada"], startdate=startdate, enddate=enddate)
        else:
            data = get_dataframe([bmark, stock], startdate=startdate, enddate=enddate)

        self.matplotlibWidget.axis.plot(data)
        self.matplotlibWidget.axis.legend([bmark, stock])

        self.matplotlibWidget.axis.yaxis.tick_right()

        # removes the frame of the plot
        self.matplotlibWidget.axis.spines['top'].set_visible(False)
        self.matplotlibWidget.axis.spines['right'].set_visible(False)
        self.matplotlibWidget.axis.spines['bottom'].set_visible(False)
        self.matplotlibWidget.axis.spines['left'].set_visible(False)

        self.matplotlibWidget.axis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.3)
        self.matplotlibWidget.axis.yaxis.set_major_formatter(PercentFormatter())
        self.matplotlibWidget.canvas.draw()

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

    # this function is for label click events
    # def doSomething(self, event):
        # print('Hey')


def get_dataframe(names, startdate, enddate):
    frame = pd.DataFrame()

    # create a DataFrame with columns being the different names
    for name in names:
        df = Dbm.get_prices(name, startdate=startdate, enddate=enddate)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        frame = pd.concat([frame, df], ignore_index=True, axis=1)

    normalized = Cmp.normalize_prices(frame)
    normalized.columns = names

    return normalized


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('MyWindow')

    main = MyWindow()
    main.show()

    sys.exit(app.exec_())
