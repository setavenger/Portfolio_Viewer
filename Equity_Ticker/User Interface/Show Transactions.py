
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem, QTableView
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel, QSqlDatabase
from PyQt5.uic import loadUi

import sqlite3
import Equity_Ticker.DatabaseManagement as Dm


class TableTransactions(QMainWindow):
    def __init__(self, sql_model):
        super(TableTransactions, self).__init__()
        loadUi('/Users/setor/PycharmProjects/Portfolio/Equity_Ticker/User Interface/'
               'UI Templates/Transactions Main.ui', self)
        self.setWindowTitle('Transaction Form')

        data = sql_model
        print(type(data))

        self.tableView.setModel(data)
        self.tableView.setWindowTitle("All Transactions")


class CustomSqlModel(QSqlQueryModel):
    def __init__(self, parent=None):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('/Users/setor/PycharmProjects/Portfolio/Equity_Ticker/Portfolio Data')
        db.open()
        QSqlQueryModel.__init__(self, parent=parent)
        self.setQuery("select * from Transactions ORDER BY Date DESC ")

    def data(self, item, role):
        if role == Qt.ForegroundRole:
            if QSqlQueryModel.data(self, self.index(item.row(), 2), Qt.DisplayRole) == 'Sell':
                return QColor(27, 120, 55)
            else:
                return QColor(227, 26, 28)
        if role == Qt.BackgroundRole:
            return QColor(217, 217, 217)
        return QSqlQueryModel.data(self, item, role)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = CustomSqlModel()
    widget = TableTransactions(model)
    widget.show()
    sys.exit(app.exec_())
