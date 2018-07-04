
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase
from PyQt5.uic import loadUi


class TableTransactions(QMainWindow):
    def __init__(self, sql_model):
        super(TableTransactions, self).__init__()
        loadUi('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/UserInterface/'
               'UI Templates/Transactions Main.ui', self)
        self.setWindowTitle('Transaction Form')

        data = sql_model

        self.tableView.setModel(data)
        self.tableView.setWindowTitle("All Transactions")


class CustomSqlModel(QSqlQueryModel):
    def __init__(self, parent=None):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Portfolio Data')
        db.open()
        QSqlQueryModel.__init__(self, parent=parent)
        self.setQuery("select * from Transactions ORDER BY Date DESC ")
        # TODO large numbers still displayed scientific

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
