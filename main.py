from multiprocessing import connection
import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import*
from PyQt5 import  QtCore
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore, QtGui
import sqlite3
import pandas as pd

import DailyConverter
import KNearestNeighbour

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        self.login.clicked.connect(self.loginFunction)
        self.login.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.create_account.clicked.connect(self.createAccount) #goes to createAccount screen
        self.create_account.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.show_hide.clicked.connect(self.toggleVisibility)
        self.error_field.setAlignment(QtCore.Qt.AlignCenter)

        


    def toggleVisibility(self):
        if self.password_field.echoMode()==(QtWidgets.QLineEdit.Password):
            self.show_hide.setStyleSheet("background-image : url(images/hide.jpg);")
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.show_hide.setStyleSheet("background-image : url(images/show.jpg);")
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
                

    def loginFunction(self):
        user = self.username_field.text()
        password = self.password_field.text()


        if len(user)==0 or len(password)==0:
            self.error_field.setText("Please input all fields.")
        else:
            connection = sqlite3.connect("user_info.db") #database connection
            cursor = connection.cursor()
            query = "SELECT password FROM user_info WHERE username =\'"+user+"\'"
            cursor.execute(query)
            result_pass = cursor.fetchone()[0]

            if result_pass == password:
                # başarılı giriş yapıldığı zaman, message box kaldırılıp bu block üzerinden sonraki sayfaya yönlendirilecek.
                message = QMessageBox()
                message.setIcon(QMessageBox.Information)
                message.setText("You have successfully logged in")
                message.setWindowTitle("Login")
                message.setStandardButtons(QMessageBox.Ok)
                message.setWindowIcon(QtGui.QIcon('images/flash.png'))
                message.exec()
                self.error_field.setText("")
                self.mainWindow()
                
            else:
                self.error_field.setText("Invalid username or password.")


    def createAccount(self):
        create = createAccountScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex()+1)



    def mainWindow(self):
        mainWindow = MatplotlibWidget()
        widget.addWidget(mainWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)



class createAccountScreen(QDialog):
    def __init__(self):
        super(createAccountScreen, self).__init__()
        loadUi("create_account.ui", self)
        self.reg.clicked.connect(self.signUp)
        self.reg.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.show_hide.clicked.connect(self.toggleVisibility_1)
        self.show_hide_2.clicked.connect(self.toggleVisibility_2)

    def toggleVisibility_1(self):
        if self.password_field.echoMode()==(QtWidgets.QLineEdit.Password):
            self.show_hide.setStyleSheet("background-image : url(images/hide.jpg);")
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.show_hide.setStyleSheet("background-image : url(images/show.jpg);")
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)

        
    def toggleVisibility_2(self):
        if self.confirm_password_field.echoMode()==(QtWidgets.QLineEdit.Password):
            self.show_hide_2.setStyleSheet("background-image : url(images/hide.jpg);")
            self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.show_hide_2.setStyleSheet("background-image : url(images/show.jpg);")
            self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)


    def signUp(self):
        user = self.username_field.text()
        password = self.password_field.text()
        confirm_password = self.confirm_password_field.text()

        if len(user)==0 or len(password)==0:
            self.error_field.setText("Please input all fields.")
            self.error_field.setText("")
        elif password != confirm_password:
            self.error_field.setText("Passwords do not match.")
            self.error_field.setText("")
        else:
            connection = sqlite3.connect("user_info.db")
            cursor = connection.cursor()
            self.createTable(cursor, connection)

            user_info = [user, password]
            cursor.execute('INSERT INTO user_info (username, password) VALUES (?,?)', user_info) #adding info to database

            message = QMessageBox()
            message.setIcon(QMessageBox.Information)
            message.setText("You have successfully registered in the system. You are redirected to the login page.")
            message.setWindowTitle("Register")
            message.setStandardButtons(QMessageBox.Ok)
            message.setWindowIcon(QtGui.QIcon('images/flash.png'))
            returnValue = message.exec()
            if returnValue == QMessageBox.Ok:
                self.login() #goes back to login screen
            
            self.error_field.setText("")

            connection.commit()
            connection.close()
        
    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def createTable(self, cursor, connection):
        cursor.execute("CREATE TABLE IF NOT EXISTS user_info (username TEXT, password TEXT)")
        connection.commit()

    



class MatplotlibWidget(QMainWindow):

    def __init__(self, parent=None):

        super(QMainWindow, self).__init__(parent)
        loadUi("mainWindow.ui", self)

        # selecting the date on the calendar if desired
        self.dateEditInput.setCalendarPopup(True)
        self.dateEditOutput.setCalendarPopup(True)

        self.houseID.setAlignment(QtCore.Qt.AlignCenter)
        self.peakTime.setAlignment(QtCore.Qt.AlignCenter)
        self.energy.setAlignment(QtCore.Qt.AlignCenter)

        self.block()
        self.percentage()

        self.graphButton.clicked.connect(self.dailyGraph)
        self.shiftingButton.clicked.connect(self.loadShifting)
        self.classificationButton.clicked.connect(self.classification)
        self.showButton.clicked.connect(self.addHousehold)

    def block(self):
        blocks = ['block_60', 'block_61',  'block_62',  'block_63', 'block_66', 'block_68', 'block_69', 'block_79']

        menu = QMenu()  # creating menu

        self.blocksButton_1.setMenu(menu)  # button turns into menu.
        self.blocksButton_2.setMenu(menu)  
        self.blocksButton_3.setMenu(menu)  
        self.blocksButton_4.setMenu(menu)  

        menu.triggered.connect(lambda x: self.blocksButton_1.setText(x.text()))  # the clicked item is written on the button
        # after selecting the item from the menu with the button, the "actionClicked" function is called.

        menu.triggered.connect(lambda x: self.blocksButton_2.setText(x.text()))

        menu.triggered.connect(lambda x: self.blocksButton_3.setText(x.text()))

        menu.triggered.connect(lambda x: self.blocksButton_4.setText(x.text()))

        menu.triggered.connect(self.actionClickedBlocks)

        # "id" and "menu" are sending to "addMenu" function
        self.addMenu(blocks, menu)

    def actionClickedBlocks(self, action):
        # the item selected from the menu is assigned to the variable "householdId"
        self.blockId = action.text()
        # print(self.blockId)
        self.household(self.blockId)

    def household(self, blockId):

        path_input = "updated-dataframes/DataFrameKNNc5_"+ blockId+ ".csv"
        householdData = pd.read_csv(path_input)  # reading csv file
        id = householdData['ID'].tolist()  # converting column data to list
        # the duplicate elements in the list are removed using the "dictionary" structure in python.
        id = list(dict.fromkeys(id))
        menu = QMenu()  # creating menu

        self.householdButton.setMenu(menu)  # button turns into menu.

        menu.triggered.connect(lambda x: self.householdButton.setText( x.text()))  # the clicked item is written on the button
        # after selecting the item from the menu with the button, the "actionClicked" function is called.
        menu.triggered.connect(self.actionClickedHouseholds)

        # "id" and "menu" are sending to "addMenu" function
        self.addMenu(id, menu)


    def actionClickedHouseholds(self, action):
        # the item selected from the menu is assigned to the variable "householdId"
        self.householdId = action.text()

    def percentage(self):
        percentages = ['30%', '40%',  '50%',  '60%', '70%']

        menu = QMenu()  # creating menu

        self.percentageButton.setMenu(menu)  # button turns into menu.

        menu.triggered.connect(lambda x: self.percentageButton.setText(x.text()))  # the clicked item is written on the button
        # after selecting the item from the menu with the button, the "actionClicked" function is called.

        menu.triggered.connect(self.actionClickedPercentages)

        # "id" and "menu" are sending to "addMenu" function
        self.addMenu(percentages, menu)

    def actionClickedPercentages(self, action):
        # the item selected from the menu is assigned to the variable "householdId"
        self.offer = action.text()
        
        # self.household(self.blockId)
        

    # in this function the households are added to the menu
    def addMenu(self, data, menuObject):
        if isinstance(data, dict):
            for i, j in data.items():
                subMenu = QMenu(i, menuObject)
                menuObject.addMenu(subMenu)
                self.addMenu(j, subMenu)

        elif isinstance(data, list):
            for element in data:
                self.addMenu(element, menuObject)

        else:
            action = menuObject.addAction(data)
            action.setIconVisibleInMenu(False)

    def dailyGraph(self):

        # sending required data to DailyConverter.py
        path_input = "input-tables/daily_dataset/"+ self.blockId+ ".csv"
        path_output = "output-tables/dfOut/"+self.blockId+ "_day_converted.csv"
        start = str(self.dateEditInput.date().toPyDate())
        end = str(self.dateEditOutput.date().toPyDate())

        DailyConverter.convert(path_input, path_output,
                               self.householdId, start, end)

        # reading the generated csv file and splitting its axes
        data = pd.read_csv(path_output)
        x = data.day
        y = data.energy_sum

        # deleting the old chart before the new chart is created
        self.matplotlib_widget.canvas.axes.clear()
        self.matplotlib_widget.canvas.axes.plot(x, y)  # plotting
        # arrangement of the way the information on the axes is written in terms of readability
        self.matplotlib_widget.canvas.axes.tick_params(labelrotation=45)
        self.matplotlib_widget.canvas.axes.set(
            xlabel="Days", ylabel="Energy Consumption (kWh)", title="Consumption of a HouseHold")
        self.matplotlib_widget.canvas.axes.grid()
        self.matplotlib_widget.canvas.draw()

    def classification(self):
        path = "updated-dataframes/DataFrameKNNc5_"+ self.blockId+ ".csv"
        KNearestNeighbour.classification(path)
        self.pixmap = QPixmap('figure_images/saved_figure_classification.png')
        self.figureLabel_1.setPixmap(self.pixmap)
        self.show()     

    def message(self):
        message = QMessageBox()
        message.setIcon(QMessageBox.Information)
        message.setText("The household successfully added.")
        message.setWindowTitle("Add New Hosehold")
        message.setStandardButtons(QMessageBox.Ok)
        message.setWindowIcon(QtGui.QIcon('images/flash.png'))
        message.exec()

    def addHousehold(self):
        path = "updated-dataframes/DataFrameKNNc5_"+ self.blockId+ ".csv"
        peak_time = float(self.peakTime.text())
        energy = float(self.energy.text())
        houseId = self.houseID.text()

        KNearestNeighbour.addHousehold(houseId, path, peak_time, energy)
        self.pixmap = QPixmap('figure_images/saved_figure_addHousehold.png')
        self.message()
        self.figureLabel_2.setPixmap(self.pixmap)
        self.show()
    
    def loadShifting(self):
        path = "updated-dataframes/DataFrameKNNc5_"+ self.blockId+ ".csv"

        KNearestNeighbour.loadShifting(path, self.offer)
        KNearestNeighbour.classification(path)
        self.pixmap1 = QPixmap('figure_images/saved_figure_beforeloadShifting.png')
        self.figureLabel_3.setPixmap(self.pixmap1)
        self.show()
        self.pixmap2 = QPixmap('figure_images/saved_figure_afterloadShifting.png')
        self.figureLabel_4.setPixmap(self.pixmap2)
        self.show()
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(login)
    widget.setFixedHeight(950)
    widget.setFixedWidth(1200)
    widget.setWindowTitle("Customer Behaviour Analysis")
    widget.setWindowIcon(QtGui.QIcon('images/flash.png'))
    widget.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
    widget.show()
    sys.exit(app.exec_())