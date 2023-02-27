from PyQt5 import QtWidgets, uic
import sys
import qdarkstyle


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        #uic.loadUi('basic.ui', self)
        uic.loadUi('tabletutorial3.ui', self)
        self.show()

        self.loaddata()
        print ("6")

        #sys.stdout = self
        self.tableWidget.setColumnWidth(1, 100)
        #self.tableWidget.setRowHeight(1, 80)
        print ("8")



    def loaddata(self):
        people = [{'name': 'John', 'age': 45, 'address' : "New Yorl"},
                {'name': 'Greg', 'age': 40, 'address' : "Oslo\n rrr"},
                {'name': 'Per', 'age': 35, 'address' : "CDMX"}]
        self.tableWidget.setRowCount(len(people))

        for row, person in enumerate(people):
            print ("7")
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(person["name"]))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(person["age"])))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(person["address"]))


        self.tableWidget.resizeRowsToContents()
        
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.setStyleSheet(qdarkstyle.load_stylesheet())
app.exec_()